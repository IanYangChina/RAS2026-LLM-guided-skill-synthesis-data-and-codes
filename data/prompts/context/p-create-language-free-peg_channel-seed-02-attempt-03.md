## Search State

- **Seed**: 2
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 4 | 0.1123 | 0.03 | ❌ rejected |
| 2 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 3 | 0.1314 | 0.00 | ❌ rejected |
| 1 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 3 | 0.2054 | 0.24 | ✅ accepted |
| 0 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 3 | 0.4670 | 0.18 | ✅ accepted |

**Proposal policy**: task_score is 0.03 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.112) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: reach_contact
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.3
- id: complete_push
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
    - 0.03
    - 0.08
    tolerance: 0.02
    orientation:
      mode: keep_current
  subtask_id: reach_contact
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.03
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 15.0
      default: 3.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
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
      distance: 0.18
      axis: world_y
      mode: add_to_offset
      sign: negative
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.12
      - 0.2
      default: 0.18
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
  - id: force_guard
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.002
    - 0.0
    - 0.0
  subtask_id: complete_push
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
    tolerance: 0.01
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.03, 0.08], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.03, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.18, mode=add_to_offset, sign=negative}, tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=40.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.002, 0.0, 0.0]
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.112
- **task_score** (E): 0.033
- **fitness_score**: 0.122  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.260

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1809 |
| contact_1 | 0.33 | 1.00 | 0.0883 |
| push_1 | 1.00 | 1.00 | 0.0206 |
| retract_1 | 1.00 | 1.00 | 0.0888 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.493, 0.127, 0.137) | (0.494, 0.068, 0.040)→(0.498, 0.068, 0.034) | 0.151→0.148 | 1.00 / 1.000 | 0.547 | 3.659 |
| contact_1 | contact | 0.33 / step_budget | (0.493, 0.127, 0.137)→(0.493, 0.118, 0.051) | (0.498, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 | 1.00 / 1.333 | 32.209 | 32.213 |
| push_1 | push | 1.00 / force_exceeded | (0.493, 0.118, 0.051)→(0.491, 0.098, 0.048) | (0.498, 0.068, 0.034)→(0.499, 0.062, 0.036) | 0.148→0.142 | 1.00 / 2.333 | 1368.918 | 43.237 |
| retract_1 | retract | 1.00 / step_budget | (0.491, 0.098, 0.048)→(0.488, 0.097, 0.137) | (0.499, 0.062, 0.036)→(0.499, 0.064, 0.034) | 0.142→0.145 | 1.00 / 1.000 | 0.548 | 123.807 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.000
- phase_score: 0.144
- phase_breakdown.reach_contact_score: 0.480
- phase_breakdown.complete_push_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.203
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.098
- **Median Q (composite search score)**: 0.067
- **K-run variance**: 0.0255
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.7
- **Final σ (mean)**: 0.347


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.58095,"average_solve_count":105.0,"average_success_count":105.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":15.64059,"push_1.push_distance":0.14903,"push_1.push_force_target":29.39196,"push_1.push_speed":0.01464},"optimized_scores":{"best_composite_score":0.06688,"best_fitness_score":0.07688,"best_task_score":0.0019},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":91.0,"contact_point_centroid":[0.47497,0.08882,0.05112],"force_p95":268.95794,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":280.78618,"mean_force":156.19587,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4868,0.08883,0.04923]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":140.0,"contact_point_centroid":[0.475,0.09733,0.04327],"force_p95":9.91655,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":13.16283,"mean_force":6.43597,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48685,0.09734,0.0414]},{"body_a":"peg","body_b":"channel_base_body","contact_count":472.0,"contact_point_centroid":[0.4958,0.06134,0.00946],"force_p95":2.07534,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.49232,"mean_force":0.6864,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48716,0.10049,0.04177]},{"body_a":"attachment","body_b":"peg","contact_count":57.0,"contact_point_centroid":[0.49152,0.08013,0.05421],"force_p95":2.4038,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.07152,"mean_force":1.36917,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48685,0.09183,0.04142]},{"body_a":"peg","body_b":"channel_base_body","contact_count":316.0,"contact_point_centroid":[0.49565,0.06373,0.00935],"force_p95":0.6374,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.57232,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48941,0.15967,0.21295]},{"body_a":"attachment","body_b":"peg","contact_count":58.0,"contact_point_centroid":[0.4903,0.07734,0.05092],"force_p95":1.04507,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.29698,"mean_force":0.44777,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48669,0.08875,0.05133]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4993,0.1979,0.29574]},{"body_a":"peg","body_b":"channel_base_body","contact_count":543.0,"contact_point_centroid":[0.4959,0.05839,0.00957],"force_p95":0.61777,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.0744,"mean_force":0.52766,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48447,0.08949,0.08525]},{"body_a":"peg","body_b":"channel_base_body","contact_count":522.0,"contact_point_centroid":[0.49497,0.06394,0.0094],"force_p95":0.55029,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5516,"mean_force":0.54559,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48443,0.1183,0.0894]}],"total_contact_groups":9},"final_pose_error":0.01162,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49549,0.06314,0.03406],"final_tcp_position":[0.48376,0.08991,0.13025],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":3920.31222,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":343.0,"n_steps_budget":1000.0,"object_pos_end":[0.49527,0.0639,0.03392],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.1441,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54903,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":344.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_contact","tcp_end":[0.48079,0.12362,0.13721],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12019,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":522.0,"n_steps_budget":600.0,"object_pos_end":[0.49518,0.06363,0.034],"object_pos_start":[0.49527,0.0639,0.03392],"object_to_goal_dist_end":0.14384,"object_to_goal_dist_start":0.1441,"object_z_max":0.034,"peak_contact_force":0.5415,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":522.0,"raw_peak_contact_force":0.5516,"subtask_id":"reach_contact","tcp_end":[0.49047,0.11372,0.0458],"tcp_start":[0.48079,0.12362,0.13721],"tcp_to_object_dist_end":0.05168,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":472.0,"n_steps_budget":1000.0,"object_pos_end":[0.49542,0.06203,0.03582],"object_pos_start":[0.49518,0.06363,0.034],"object_to_goal_dist_end":0.14216,"object_to_goal_dist_start":0.14384,"object_z_max":0.03581,"peak_contact_force":3920.31222,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":669.0,"raw_peak_contact_force":13.16283,"subtask_id":"complete_push","tcp_end":[0.48685,0.09046,0.04144],"tcp_start":[0.49047,0.11372,0.0458],"tcp_to_object_dist_end":0.03022,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":544.0,"n_steps_budget":630.0,"object_pos_end":[0.49549,0.06314,0.03406],"object_pos_start":[0.49542,0.06203,0.03582],"object_to_goal_dist_end":0.14334,"object_to_goal_dist_start":0.14216,"object_z_max":0.0364,"peak_contact_force":0.5484,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":692.0,"raw_peak_contact_force":280.78618,"tcp_end":[0.48376,0.08991,0.13025],"tcp_start":[0.48685,0.09046,0.04144],"tcp_to_object_dist_end":0.10054,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.85542,"average_solve_count":83.0,"average_success_count":83.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":11.85001,"push_1.push_distance":0.15952,"push_1.push_force_target":30.4178,"push_1.push_speed":0.01385},"optimized_scores":{"best_composite_score":0.32659,"best_fitness_score":0.08659,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.47499,0.10444,0.0599],"force_p95":112.19983,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":112.19983,"mean_force":112.19983,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48529,0.11029,0.05833]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.475,0.10431,0.05998],"force_p95":95.53674,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":95.53674,"mean_force":95.53674,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48523,0.1103,0.05849]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":4.0,"contact_point_centroid":[0.47499,0.10463,0.05991],"force_p95":79.31194,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":79.40051,"mean_force":73.36243,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48543,0.11021,0.05832]},{"body_a":"peg","body_b":"channel_base_body","contact_count":321.0,"contact_point_centroid":[0.49462,0.05908,0.00933],"force_p95":0.61216,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.59176,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48284,0.15711,0.21239]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49866,0.19708,0.29412]},{"body_a":"peg","body_b":"channel_base_body","contact_count":482.0,"contact_point_centroid":[0.49417,0.05894,0.00939],"force_p95":0.55039,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.54615,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47548,0.11437,0.0962]},{"body_a":"peg","body_b":"channel_base_body","contact_count":543.0,"contact_point_centroid":[0.49412,0.05876,0.0094],"force_p95":0.55039,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55295,"mean_force":0.54572,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48243,0.10959,0.10211]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.48134,0.07161,0.00939],"force_p95":0.54477,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54477,"mean_force":0.54477,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48529,0.11029,0.05833]}],"total_contact_groups":8},"final_pose_error":0.01163,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49435,0.0591,0.03399],"final_tcp_position":[0.48239,0.10962,0.14706],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":112.19983,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":350.0,"n_steps_budget":1000.0,"object_pos_end":[0.49403,0.05898,0.03385],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13925,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54521,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":356.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_contact","tcp_end":[0.46839,0.11909,0.13696],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12208,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":482.0,"n_steps_budget":630.0,"object_pos_end":[0.49401,0.05907,0.0339],"object_pos_start":[0.49403,0.05898,0.03385],"object_to_goal_dist_end":0.13933,"object_to_goal_dist_start":0.13925,"object_z_max":0.0339,"peak_contact_force":95.53674,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":483.0,"raw_peak_contact_force":95.53674,"subtask_id":"reach_contact","tcp_end":[0.48529,0.11029,0.05833],"tcp_start":[0.46839,0.11909,0.13696],"tcp_to_object_dist_end":0.05741,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49398,0.05902,0.0339],"object_pos_start":[0.49401,0.05907,0.0339],"object_to_goal_dist_end":0.13929,"object_to_goal_dist_start":0.13933,"object_z_max":0.0339,"peak_contact_force":112.19983,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":112.19983,"subtask_id":"complete_push","tcp_end":[0.48536,0.11026,0.05829],"tcp_start":[0.48529,0.11029,0.05833],"tcp_to_object_dist_end":0.0574,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.49435,0.0591,0.03399],"object_pos_start":[0.49398,0.05902,0.0339],"object_to_goal_dist_end":0.13934,"object_to_goal_dist_start":0.13929,"object_z_max":0.03399,"peak_contact_force":0.54594,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":547.0,"raw_peak_contact_force":79.40051,"tcp_end":[0.48239,0.10962,0.14706],"tcp_start":[0.48536,0.11026,0.05829],"tcp_to_object_dist_end":0.12442,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.65741,"average_solve_count":108.0,"average_success_count":108.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":5.00348,"push_1.push_distance":0.19937,"push_1.push_force_target":35.76211,"push_1.push_speed":0.01459},"optimized_scores":{"best_composite_score":-0.05656,"best_fitness_score":0.20344,"best_task_score":0.09788},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":543.0,"contact_point_centroid":[0.50602,0.06587,0.00958],"force_p95":0.6591,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.23477,"mean_force":0.54459,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49763,0.09283,0.08744]},{"body_a":"attachment","body_b":"peg","contact_count":55.0,"contact_point_centroid":[0.50166,0.08147,0.05388],"force_p95":2.38606,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.95734,"mean_force":0.69443,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49821,0.0929,0.05448]},{"body_a":"peg","body_b":"channel_base_body","contact_count":611.0,"contact_point_centroid":[0.50639,0.06925,0.00967],"force_p95":3.86788,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.34859,"mean_force":1.82581,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50103,0.11056,0.04407]},{"body_a":"peg","body_b":"channel_base_body","contact_count":314.0,"contact_point_centroid":[0.50555,0.08092,0.00934],"force_p95":0.57757,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.59536,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51446,0.16732,0.21223]},{"body_a":"attachment","body_b":"peg","contact_count":306.0,"contact_point_centroid":[0.50328,0.0902,0.04419],"force_p95":3.67562,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.01326,"mean_force":2.74822,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50078,0.1019,0.0438]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50077,0.19765,0.29383]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":73.0,"contact_point_centroid":[0.52507,0.06784,0.05959],"force_p95":1.25861,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.57274,"mean_force":0.24834,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49757,0.09282,0.069]},{"body_a":"peg","body_b":"channel_base_body","contact_count":373.0,"contact_point_centroid":[0.50598,0.08082,0.00938],"force_p95":0.55007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55023,"mean_force":0.54677,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5157,0.13435,0.09182]}],"total_contact_groups":8},"final_pose_error":0.01188,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5068,0.07074,0.03381],"final_tcp_position":[0.49767,0.09286,0.13244],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":74.24045,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":343.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.08086,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54597,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":350.0,"raw_peak_contact_force":4.32595,"subtask_id":"reach_contact","tcp_end":[0.52851,0.13857,0.13661],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12005,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":373.0,"n_steps_budget":630.0,"object_pos_end":[0.50596,0.08087,0.03378],"object_pos_start":[0.50598,0.08086,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16109,"object_z_max":0.03378,"peak_contact_force":0.54819,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":373.0,"raw_peak_contact_force":0.55023,"subtask_id":"reach_contact","tcp_end":[0.50458,0.1307,0.04852],"tcp_start":[0.52851,0.13857,0.13661],"tcp_to_object_dist_end":0.05199,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":612.0,"n_steps_budget":1000.0,"object_pos_end":[0.50695,0.06493,0.03841],"object_pos_start":[0.50596,0.08087,0.03378],"object_to_goal_dist_end":0.1451,"object_to_goal_dist_start":0.1611,"object_z_max":0.0384,"peak_contact_force":74.24045,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":917.0,"raw_peak_contact_force":4.34859,"subtask_id":"complete_push","tcp_end":[0.50082,0.09343,0.04388],"tcp_start":[0.50458,0.1307,0.04852],"tcp_to_object_dist_end":0.02966,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":544.0,"n_steps_budget":630.0,"object_pos_end":[0.5068,0.07074,0.03381],"object_pos_start":[0.50695,0.06493,0.03841],"object_to_goal_dist_end":0.15102,"object_to_goal_dist_start":0.1451,"object_z_max":0.03856,"peak_contact_force":0.54823,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":671.0,"raw_peak_contact_force":11.23477,"tcp_end":[0.49767,0.09286,0.13244],"tcp_start":[0.50082,0.09343,0.04388],"tcp_to_object_dist_end":0.1015,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```