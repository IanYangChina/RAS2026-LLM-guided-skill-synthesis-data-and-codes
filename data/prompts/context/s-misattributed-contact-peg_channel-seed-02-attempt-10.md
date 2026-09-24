## Search State

- **Seed**: 2
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.3436 | 0.34 | ❌ rejected |
| 9 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 6 | -0.2048 | 0.00 | ❌ rejected |
| 8 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.1257 | 0.06 | ❌ rejected |
| 7 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.3486 | 0.33 | ❌ rejected |
| 6 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.3781 | 0.41 | ✅ accepted |

**Proposal policy**: task_score is 0.34 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.344) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: reach_contact
  anchor: object
  offset:
  - 0.0
  - 0.02
  - 0.005
  weight: 0.3
- id: push_channel
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_above_peg
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
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: reach_contact
- id: descend_contact
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.02
    - 0.005
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_backset_y:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.y
        mode: replace
    descend_lateral_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: replace
  guards:
  - id: guard_contact
    when: after_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: abort
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: reach_contact
- id: push_to_goal
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.005
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 1
    strategy: reduce_speed
  subtask_id: push_channel

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_above_peg** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.05, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
  - retries: max_attempts=0, strategy=repeat
- **descend_contact** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.02, 0.005], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_backset_y: status=consumed; consumers=target.offset.y (replace)
    - descend_lateral_x: status=consumed; consumers=target.offset.x (replace)
  - guards:
    - id=guard_contact, when=after_phase, predicate=contact_detected, on_failure=abort, threshold=1.0
  - retries: max_attempts=0, strategy=repeat
- **push_to_goal** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.005], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=1, strategy=reduce_speed

## Design Metrics

- **Composite score**: 0.344
- **task_score** (E): 0.336
- **fitness_score**: 0.624  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above_peg | 1.00 | 1.00 | 0.1671 |
| descend_contact | 1.00 | 1.00 | 0.1155 |
| push_through_channel | 0.00 | 1.00 | 0.0268 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.493, 0.128, 0.152) | (0.494, 0.068, 0.040)→(0.498, 0.068, 0.034) | 0.151→0.148 | 1.00 / 1.000 | 0.546 | 61.723 |
| descend_contact | descend | 1.00 / step_budget | (0.493, 0.128, 0.152)→(0.495, 0.099, 0.042) | (0.498, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 | 1.00 / 4.000 | 251.319 | 2598.700 |
| push_through_channel | push | 0.00 / step_budget | (0.495, 0.099, 0.042)→(0.510, 0.081, 0.051) | (0.498, 0.068, 0.034)→(0.498, -0.069, 0.028) | 0.148→0.017 | 1.00 / 1.000 | 0.547 | 3.659 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.816
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.537
- phase_score: 0.853
- phase_breakdown.reach_contact_score: 0.858
- phase_breakdown.push_channel_score: 0.851

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.727
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.537
- **Median Q (composite search score)**: 0.305
- **K-run variance**: 0.0054
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.195


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.54167,"average_solve_count":120.0,"average_success_count":120.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_peg.approach_height":0.0898,"descend_contact.descend_backset_y":0.02903,"descend_contact.descend_lateral_x":-0.00247,"push_through_channel.push_speed":0.03182,"push_through_channel.push_stroke_distance":0.15611},"optimized_scores":{"best_composite_score":0.44655,"best_fitness_score":0.72655,"best_task_score":0.53716},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":134.0,"contact_point_centroid":[0.53183,0.11715,0.05961],"force_p95":1523.0145,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3469.94877,"mean_force":531.0954,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50189,0.07995,0.0468]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":13.0,"contact_point_centroid":[0.52552,0.08007,0.05978],"force_p95":2993.75138,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3168.29014,"mean_force":1556.48745,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50816,0.07182,0.02429]},{"body_a":"world","body_b":"link7","contact_count":799.0,"contact_point_centroid":[0.49871,0.14252,-6e-05],"force_p95":237.92276,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":335.13024,"mean_force":223.73415,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50198,0.08239,0.05102]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":820.0,"contact_point_centroid":[0.46962,0.11993,0.06],"force_p95":305.84787,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":328.6342,"mean_force":225.31364,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50192,0.08235,0.05095]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":8.0,"contact_point_centroid":[0.47488,0.09922,0.05917],"force_p95":168.59593,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":184.06404,"mean_force":71.41207,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.48649,0.10009,0.05741]},{"body_a":"attachment","body_b":"peg","contact_count":7.0,"contact_point_centroid":[0.49618,0.0772,0.04113],"force_p95":49.55098,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":59.16581,"mean_force":23.45771,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49502,0.0884,0.03699]},{"body_a":"peg","body_b":"channel_base_body","contact_count":942.0,"contact_point_centroid":[0.49878,-0.06506,0.00807],"force_p95":0.79251,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":58.17272,"mean_force":0.83665,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50171,0.08236,0.05077]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":16.0,"contact_point_centroid":[0.47499,-0.04323,0.02429],"force_p95":8.54309,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.77285,"mean_force":3.32961,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50303,0.08308,0.05125]},{"body_a":"peg","body_b":"channel_base_body","contact_count":300.0,"contact_point_centroid":[0.49584,0.0638,0.00935],"force_p95":0.64698,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.5737,"phase_index":0.0,"phase_name":"approach_above_peg","phase_type":"approach","tcp_position_centroid":[0.48949,0.15988,0.21784]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":27.0,"contact_point_centroid":[0.52552,0.0021,0.03238],"force_p95":1.7769,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.33874,"mean_force":0.74533,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50596,0.07382,0.03068]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_above_peg","phase_type":"approach","tcp_position_centroid":[0.49927,0.19781,0.29576]},{"body_a":"peg","body_b":"channel_base_body","contact_count":358.0,"contact_point_centroid":[0.49481,0.06386,0.0094],"force_p95":0.5502,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55295,"mean_force":0.54571,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.48334,0.10996,0.09373]}],"total_contact_groups":12},"final_pose_error":0.14755,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49429,-0.06667,0.02415],"final_tcp_position":[0.50411,0.08386,0.05115],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":3469.94877,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":327.0,"n_steps_budget":1000.0,"object_pos_end":[0.49516,0.06403,0.03391],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14424,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54412,"phase_name":"approach_above_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":366.0,"raw_peak_contact_force":184.06404,"subtask_id":"reach_contact","tcp_end":[0.48097,0.12417,0.14686],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12874,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":358.0,"n_steps_budget":750.0,"object_pos_end":[0.49525,0.0637,0.03396],"object_pos_start":[0.49516,0.06403,0.03391],"object_to_goal_dist_end":0.1439,"object_to_goal_dist_start":0.14424,"object_z_max":0.03397,"peak_contact_force":241.30179,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2758.0,"raw_peak_contact_force":3469.94877,"subtask_id":"reach_contact","tcp_end":[0.48805,0.09583,0.04212],"tcp_start":[0.48097,0.12417,0.14686],"tcp_to_object_dist_end":0.03392,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49429,-0.06667,0.02415],"object_pos_start":[0.49525,0.0637,0.03396],"object_to_goal_dist_end":0.02148,"object_to_goal_dist_start":0.1439,"object_z_max":0.04063,"peak_contact_force":0.54729,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":328.0,"raw_peak_contact_force":2.44546,"subtask_id":"push_channel","tcp_end":[0.50411,0.08386,0.05115],"tcp_start":[0.48805,0.09583,0.04212],"tcp_to_object_dist_end":0.15325,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.30952,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_peg.approach_height":0.10538,"descend_contact.descend_backset_y":0.03005,"descend_contact.descend_lateral_x":0.00599,"push_through_channel.push_speed":0.02047,"push_through_channel.push_stroke_distance":0.15498},"optimized_scores":{"best_composite_score":0.30477,"best_fitness_score":0.58477,"best_task_score":0.23296},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":147.0,"contact_point_centroid":[0.53428,0.11655,0.05972],"force_p95":1547.01353,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2962.2033,"mean_force":499.51811,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50572,0.07808,0.05059]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52603,0.07572,0.05982],"force_p95":2591.61543,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2754.05654,"mean_force":1323.94065,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50886,0.06889,0.02602]},{"body_a":"world","body_b":"link7","contact_count":783.0,"contact_point_centroid":[0.50699,0.14139,-6e-05],"force_p95":231.97053,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":435.41113,"mean_force":221.14949,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51011,0.08092,0.05062]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":804.0,"contact_point_centroid":[0.47497,0.11995,0.05283],"force_p95":250.81169,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":297.7265,"mean_force":194.34583,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51,0.08091,0.05059]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.49627,0.07545,0.0383],"force_p95":48.63998,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":51.07891,"mean_force":33.1753,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49751,0.08709,0.03792]},{"body_a":"peg","body_b":"channel_base_body","contact_count":937.0,"contact_point_centroid":[0.49601,-0.05225,0.00992],"force_p95":0.75042,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":47.95137,"mean_force":0.53491,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50928,0.08081,0.05127]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":11.0,"contact_point_centroid":[0.52535,0.00888,0.03113],"force_p95":7.01374,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.62231,"mean_force":2.11678,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50795,0.06754,0.02738]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":6.0,"contact_point_centroid":[0.47499,-0.00911,0.05954],"force_p95":6.29465,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.31282,"mean_force":2.60228,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50683,0.07318,0.04067]},{"body_a":"peg","body_b":"channel_base_body","contact_count":281.0,"contact_point_centroid":[0.49456,0.0591,0.00932],"force_p95":0.64567,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.59823,"phase_index":0.0,"phase_name":"approach_above_peg","phase_type":"approach","tcp_position_centroid":[0.48312,0.15759,0.22494]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_above_peg","phase_type":"approach","tcp_position_centroid":[0.49853,0.19677,0.29429]},{"body_a":"peg","body_b":"channel_base_body","contact_count":843.0,"contact_point_centroid":[0.49607,-0.10003,0.02857],"force_p95":0.35298,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.87304,"mean_force":0.2172,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50981,0.0809,0.05078]},{"body_a":"peg","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.50867,0.0437,0.07016],"force_p95":0.54615,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.55373,"mean_force":0.47794,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51,0.06967,0.02389]},{"body_a":"peg","body_b":"channel_base_body","contact_count":440.0,"contact_point_centroid":[0.49405,0.0589,0.00939],"force_p95":0.55035,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55326,"mean_force":0.54619,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.48006,0.10574,0.10043]}],"total_contact_groups":13},"final_pose_error":0.14964,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49673,-0.07036,0.03542],"final_tcp_position":[0.5128,0.08136,0.05062],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":2962.2033,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":310.0,"n_steps_budget":1000.0,"object_pos_end":[0.49405,0.0589,0.03384],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13916,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.5456,"phase_name":"approach_above_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":440.0,"raw_peak_contact_force":0.55326,"subtask_id":"reach_contact","tcp_end":[0.46906,0.12047,0.16156],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14397,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":440.0,"n_steps_budget":870.0,"object_pos_end":[0.49412,0.05881,0.03389],"object_pos_start":[0.49405,0.0589,0.03384],"object_to_goal_dist_end":0.13907,"object_to_goal_dist_start":0.13916,"object_z_max":0.03389,"peak_contact_force":219.49581,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3555.0,"raw_peak_contact_force":2962.2033,"subtask_id":"reach_contact","tcp_end":[0.49356,0.09114,0.04085],"tcp_start":[0.46906,0.12047,0.16156],"tcp_to_object_dist_end":0.03308,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49673,-0.07036,0.03542],"object_pos_start":[0.49412,0.05881,0.03389],"object_to_goal_dist_end":0.01116,"object_to_goal_dist_start":0.13907,"object_z_max":0.0485,"peak_contact_force":0.549,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":316.0,"raw_peak_contact_force":4.20518,"subtask_id":"push_channel","tcp_end":[0.5128,0.08136,0.05062],"tcp_start":[0.49356,0.09114,0.04085],"tcp_to_object_dist_end":0.15332,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.26154,"average_solve_count":130.0,"average_success_count":130.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_peg.approach_height":0.09111,"descend_contact.descend_backset_y":0.0272,"descend_contact.descend_lateral_x":-0.00337,"push_through_channel.push_speed":0.0243,"push_through_channel.push_stroke_distance":0.15909},"optimized_scores":{"best_composite_score":0.27946,"best_fitness_score":0.55946,"best_task_score":0.23886},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":396.0,"contact_point_centroid":[0.5252,0.08141,0.05157],"force_p95":287.3024,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1363.94913,"mean_force":177.72738,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51313,0.08039,0.05017]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":333.0,"contact_point_centroid":[0.52827,0.11995,0.05998],"force_p95":398.33728,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":686.21848,"mean_force":161.86775,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51133,0.08102,0.04946]},{"body_a":"world","body_b":"link7","contact_count":859.0,"contact_point_centroid":[0.50965,0.14179,-7e-05],"force_p95":344.53399,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":406.15909,"mean_force":283.2301,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51198,0.08133,0.05064]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":59.0,"contact_point_centroid":[0.47498,0.11997,0.05453],"force_p95":313.94146,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":353.31368,"mean_force":214.63676,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51315,0.07912,0.05108]},{"body_a":"peg","body_b":"channel_base_body","contact_count":929.0,"contact_point_centroid":[0.49938,-0.06692,0.00824],"force_p95":1.04251,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":164.77703,"mean_force":1.07966,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.5115,0.08193,0.05017]},{"body_a":"attachment","body_b":"peg","contact_count":6.0,"contact_point_centroid":[0.50661,0.09516,0.04467],"force_p95":152.32797,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":161.53264,"mean_force":60.90908,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50642,0.10703,0.04006]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":27.0,"contact_point_centroid":[0.52566,0.01576,0.04789],"force_p95":6.55847,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.02671,"mean_force":1.48491,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.5135,0.09215,0.04137]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":33.0,"contact_point_centroid":[0.4749,-0.03826,0.04027],"force_p95":5.92209,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.20027,"mean_force":1.86924,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50796,0.08527,0.0471]},{"body_a":"peg","body_b":"channel_base_body","contact_count":295.0,"contact_point_centroid":[0.50547,0.08095,0.00934],"force_p95":0.58712,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.59849,"phase_index":0.0,"phase_name":"approach_above_peg","phase_type":"approach","tcp_position_centroid":[0.51443,0.1675,0.21779]},{"body_a":"peg","body_b":"channel_base_body","contact_count":81.0,"contact_point_centroid":[0.48609,-0.10004,0.0252],"force_p95":0.75529,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88714,"mean_force":0.29465,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51094,0.08356,0.05086]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_above_peg","phase_type":"approach","tcp_position_centroid":[0.50082,0.19755,0.2939]},{"body_a":"peg","body_b":"channel_base_body","contact_count":320.0,"contact_point_centroid":[0.50603,0.08079,0.00938],"force_p95":0.55007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55023,"mean_force":0.54677,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.51463,0.12525,0.09514]}],"total_contact_groups":12},"final_pose_error":0.12872,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50287,-0.07079,0.02413],"final_tcp_position":[0.51316,0.07913,0.05108],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":1363.94913,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":324.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.08087,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54819,"phase_name":"approach_above_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":320.0,"raw_peak_contact_force":0.55023,"subtask_id":"reach_contact","tcp_end":[0.52832,0.13912,0.14766],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12985,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":320.0,"n_steps_budget":780.0,"object_pos_end":[0.50596,0.08087,0.03378],"object_pos_start":[0.50599,0.08087,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.1611,"object_z_max":0.03378,"peak_contact_force":293.1608,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2723.0,"raw_peak_contact_force":1363.94913,"subtask_id":"reach_contact","tcp_end":[0.50223,0.11117,0.04324],"tcp_start":[0.52832,0.13912,0.14766],"tcp_to_object_dist_end":0.03196,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50287,-0.07079,0.02413],"object_pos_start":[0.50596,0.08087,0.03378],"object_to_goal_dist_end":0.01857,"object_to_goal_dist_start":0.1611,"object_z_max":0.0527,"peak_contact_force":0.54473,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":331.0,"raw_peak_contact_force":4.32595,"subtask_id":"push_channel","tcp_end":[0.51316,0.07913,0.05108],"tcp_start":[0.50223,0.11117,0.04324],"tcp_to_object_dist_end":0.15267,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```