## Search State

- **Seed**: 2
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.1257 | 0.06 | ❌ rejected |
| 7 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.3486 | 0.33 | ❌ rejected |
| 6 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.3781 | 0.41 | ✅ accepted |
| 5 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.3268 | 0.30 | ✅ accepted |
| 4 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.2462 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.06 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.126) — your mutation base

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

- **Composite score**: 0.126
- **task_score** (E): 0.061
- **fitness_score**: 0.184  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.222
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above_peg | 1.00 | 1.00 | 0.1567 |
| descend_contact | 1.00 | 1.00 | 0.1244 |
| push_to_goal | 0.67 | 1.00 | 0.0206 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.493, 0.129, 0.163) | (0.494, 0.068, 0.040)→(0.498, 0.068, 0.034) | 0.151→0.148 | 1.00 / 1.000 | 0.000 | 262.389 |
| descend_contact | descend | 1.00 / step_budget | (0.493, 0.129, 0.163)→(0.498, 0.089, 0.047) | (0.498, 0.068, 0.034)→(0.502, 0.051, 0.040) | 0.148→0.131 | 1.00 / 1.667 | 517.410 | 466.330 |
| push_to_goal | push | 0.67 / force_exceeded | (0.498, 0.089, 0.047)→(0.509, 0.075, 0.036) | (0.502, 0.051, 0.040)→(0.502, 0.037, 0.041) | 0.131→0.117 | 1.00 / 1.000 | 0.547 | 3.659 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.218
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.100
- phase_score: 0.320
- phase_breakdown.reach_contact_score: 0.719
- phase_breakdown.push_channel_score: 0.149

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.232
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.100
- **Median Q (composite search score)**: 0.235
- **K-run variance**: 0.0366
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.135


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90278,"average_solve_count":72.0,"average_success_count":72.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_peg.approach_height":0.1276,"descend_contact.descend_backset_y":0.0172,"push_to_goal.lateral_offset_x":0.00359,"push_to_goal.push_force_threshold":32.81877,"push_to_goal.push_speed":0.02883},"optimized_scores":{"best_composite_score":0.28524,"best_fitness_score":0.2319,"best_task_score":0.09976},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":361.0,"contact_point_centroid":[0.49632,0.06436,0.00932],"force_p95":145.86258,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":159.90803,"mean_force":12.1886,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.48547,0.10569,0.11293]},{"body_a":"attachment","body_b":"peg","contact_count":36.0,"contact_point_centroid":[0.49966,0.08064,0.05602],"force_p95":157.70564,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":159.40256,"mean_force":116.95271,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.49153,0.08849,0.05549]},{"body_a":"attachment","body_b":"peg","contact_count":7.0,"contact_point_centroid":[0.50274,0.06279,0.0401],"force_p95":4.61386,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.78973,"mean_force":1.74016,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50401,0.07329,0.03767]},{"body_a":"peg","body_b":"channel_base_body","contact_count":241.0,"contact_point_centroid":[0.49581,0.0637,0.00934],"force_p95":0.6892,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.58054,"phase_index":0.0,"phase_name":"approach_above_peg","phase_type":"approach","tcp_position_centroid":[0.48981,0.16062,0.23627]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_above_peg","phase_type":"approach","tcp_position_centroid":[0.49915,0.19743,0.29596]},{"body_a":"peg","body_b":"channel_base_body","contact_count":2.0,"contact_point_centroid":[0.49925,0.04649,0.00984],"force_p95":0.0,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49371,0.08605,0.04726]}],"total_contact_groups":6},"final_pose_error":0.148,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50159,0.02896,0.03957],"final_tcp_position":[0.50804,0.06727,0.03102],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":159.90803,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":268.0,"n_steps_budget":990.0,"object_pos_end":[0.49526,0.06388,0.0339],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14409,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.0,"phase_name":"approach_above_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":397.0,"raw_peak_contact_force":159.90803,"subtask_id":"reach_contact","tcp_end":[0.48169,0.12633,0.18302],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.16223,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":361.0,"n_steps_budget":990.0,"object_pos_end":[0.49901,0.04803,0.04023],"object_pos_start":[0.49526,0.06388,0.0339],"object_to_goal_dist_end":0.12803,"object_to_goal_dist_start":0.14409,"object_z_max":0.03973,"peak_contact_force":75.08892,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9.0,"raw_peak_contact_force":5.78973,"subtask_id":"reach_contact","tcp_end":[0.49362,0.08623,0.0475],"tcp_start":[0.48169,0.12633,0.18302],"tcp_to_object_dist_end":0.03926,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":14.0,"n_steps_budget":1000.0,"object_pos_end":[0.50159,0.02896,0.03957],"object_pos_start":[0.49901,0.04803,0.04023],"object_to_goal_dist_end":0.10897,"object_to_goal_dist_start":0.12803,"object_z_max":0.04259,"peak_contact_force":0.54758,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":269.0,"raw_peak_contact_force":2.44546,"subtask_id":"push_channel","tcp_end":[0.50804,0.06727,0.03102],"tcp_start":[0.49362,0.08623,0.0475],"tcp_to_object_dist_end":0.03978,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90411,"average_solve_count":73.0,"average_success_count":73.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_peg.approach_height":0.09334,"descend_contact.descend_backset_y":0.01295,"push_to_goal.lateral_offset_x":0.00482,"push_to_goal.push_force_threshold":37.9138,"push_to_goal.push_speed":0.02958},"optimized_scores":{"best_composite_score":0.23537,"best_fitness_score":0.18203,"best_task_score":0.04635},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":11.0,"contact_point_centroid":[0.47488,0.07975,0.05947],"force_p95":477.88048,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":478.38622,"mean_force":250.31804,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.48574,0.08329,0.05774]},{"body_a":"peg","body_b":"channel_base_body","contact_count":314.0,"contact_point_centroid":[0.49626,0.06019,0.00923],"force_p95":160.41884,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":198.36192,"mean_force":21.75781,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.4783,0.09796,0.09448]},{"body_a":"attachment","body_b":"peg","contact_count":57.0,"contact_point_centroid":[0.498,0.07533,0.05556],"force_p95":168.88014,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":197.60142,"mean_force":116.9879,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.48883,0.08213,0.05507]},{"body_a":"attachment","body_b":"peg","contact_count":6.0,"contact_point_centroid":[0.50167,0.05626,0.04046],"force_p95":9.15954,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.58852,"mean_force":3.44208,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50113,0.06753,0.03929]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":5.0,"contact_point_centroid":[0.52538,0.01886,0.05663],"force_p95":5.94843,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.25495,"mean_force":3.39006,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49763,0.07223,0.04226]},{"body_a":"peg","body_b":"channel_base_body","contact_count":300.0,"contact_point_centroid":[0.49453,0.05885,0.00933],"force_p95":0.63343,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.59494,"phase_index":0.0,"phase_name":"approach_above_peg","phase_type":"approach","tcp_position_centroid":[0.48298,0.15735,0.21899]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_above_peg","phase_type":"approach","tcp_position_centroid":[0.4986,0.19693,0.29421]},{"body_a":"peg","body_b":"channel_base_body","contact_count":2.0,"contact_point_centroid":[0.50204,0.04057,0.00959],"force_p95":0.0,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49292,0.0784,0.04658]}],"total_contact_groups":8},"final_pose_error":0.14161,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50255,0.02453,0.04017],"final_tcp_position":[0.50534,0.0612,0.03422],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":478.38622,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":329.0,"n_steps_budget":1000.0,"object_pos_end":[0.49422,0.05894,0.03385],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13919,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.0,"phase_name":"approach_above_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":382.0,"raw_peak_contact_force":478.38622,"subtask_id":"reach_contact","tcp_end":[0.46872,0.11976,0.14988],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13346,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":314.0,"n_steps_budget":810.0,"object_pos_end":[0.50173,0.04168,0.0397],"object_pos_start":[0.49422,0.05894,0.03385],"object_to_goal_dist_end":0.12169,"object_to_goal_dist_start":0.13919,"object_z_max":0.03911,"peak_contact_force":93.52966,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":13.0,"raw_peak_contact_force":9.58852,"subtask_id":"reach_contact","tcp_end":[0.49282,0.07859,0.04682],"tcp_start":[0.46872,0.11976,0.14988],"tcp_to_object_dist_end":0.03864,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":12.0,"n_steps_budget":1000.0,"object_pos_end":[0.50255,0.02453,0.04017],"object_pos_start":[0.50173,0.04168,0.0397],"object_to_goal_dist_end":0.10456,"object_to_goal_dist_start":0.12169,"object_z_max":0.04234,"peak_contact_force":0.54764,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":335.0,"raw_peak_contact_force":4.20518,"subtask_id":"push_channel","tcp_end":[0.50534,0.0612,0.03422],"tcp_start":[0.49282,0.07859,0.04682],"tcp_to_object_dist_end":0.03726,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92857,"average_solve_count":70.0,"average_success_count":70.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_peg.approach_height":0.10105,"descend_contact.descend_backset_y":0.01644,"push_to_goal.lateral_offset_x":-0.00575,"push_to_goal.push_force_threshold":36.30504,"push_to_goal.push_speed":0.02635},"optimized_scores":{"best_composite_score":-0.14344,"best_fitness_score":0.13656,"best_task_score":0.03736},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52541,0.09898,0.05994],"force_p95":1383.61061,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1383.61061,"mean_force":1383.61061,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.51146,0.09873,0.0435]},{"body_a":"peg","body_b":"channel_base_body","contact_count":282.0,"contact_point_centroid":[0.50684,0.08084,0.00925],"force_p95":131.54641,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":148.87257,"mean_force":13.66846,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.51625,0.12065,0.09961]},{"body_a":"attachment","body_b":"peg","contact_count":36.0,"contact_point_centroid":[0.51404,0.0955,0.05541],"force_p95":146.17256,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":148.26472,"mean_force":102.96134,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.50876,0.10558,0.05496]},{"body_a":"peg","body_b":"channel_base_body","contact_count":278.0,"contact_point_centroid":[0.5055,0.08092,0.00934],"force_p95":0.60392,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.60165,"phase_index":0.0,"phase_name":"approach_above_peg","phase_type":"approach","tcp_position_centroid":[0.51439,0.16768,0.22275]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_above_peg","phase_type":"approach","tcp_position_centroid":[0.50088,0.19744,0.29393]},{"body_a":"peg","body_b":"channel_base_body","contact_count":2.0,"contact_point_centroid":[0.50362,0.06317,0.00967],"force_p95":0.0,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50839,0.10283,0.04682]}],"total_contact_groups":6},"final_pose_error":0.17836,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50263,0.05688,0.04232],"final_tcp_position":[0.51214,0.09744,0.04267],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":1383.61061,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":307.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.08086,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.0,"phase_name":"approach_above_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":318.0,"raw_peak_contact_force":148.87257,"subtask_id":"reach_contact","tcp_end":[0.52814,0.13962,0.15742],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13868,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":282.0,"n_steps_budget":840.0,"object_pos_end":[0.50377,0.06396,0.03988],"object_pos_start":[0.50598,0.08086,0.03378],"object_to_goal_dist_end":0.14401,"object_to_goal_dist_start":0.16109,"object_z_max":0.03934,"peak_contact_force":1383.61061,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3.0,"raw_peak_contact_force":1383.61061,"subtask_id":"reach_contact","tcp_end":[0.50833,0.10302,0.04706],"tcp_start":[0.52814,0.13962,0.15742],"tcp_to_object_dist_end":0.03998,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":6.0,"n_steps_budget":1000.0,"object_pos_end":[0.50263,0.05688,0.04232],"object_pos_start":[0.50377,0.06396,0.03988],"object_to_goal_dist_end":0.13693,"object_to_goal_dist_start":0.14401,"object_z_max":0.04201,"peak_contact_force":0.5464,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":314.0,"raw_peak_contact_force":4.32595,"subtask_id":"push_channel","tcp_end":[0.51214,0.09744,0.04267],"tcp_start":[0.50833,0.10302,0.04706],"tcp_to_object_dist_end":0.04166,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```