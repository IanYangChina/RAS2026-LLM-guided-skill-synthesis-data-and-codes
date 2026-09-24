## Search State

- **Seed**: 2
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | force_exceeded | 6 | 0.0604 | 0.10 | ❌ rejected |
| 12 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.4217 | 0.43 | ✅ accepted |
| 11 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.1880 | 0.00 | ❌ rejected |
| 10 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.3436 | 0.34 | ❌ rejected |
| 9 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 6 | -0.2048 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.10 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.060) — your mutation base

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

- **Composite score**: 0.060
- **task_score** (E): 0.100
- **fitness_score**: 0.279  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.111
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above_peg | 1.00 | 1.00 | 0.1695 |
| descend_to_contact | 0.00 | 1.00 | 0.1168 |
| push_to_goal | 1.00 | 1.00 | 0.0406 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.493, 0.106, 0.161) | (0.494, 0.068, 0.040)→(0.498, 0.068, 0.034) | 0.151→0.148 | 1.00 / 1.000 | 0.377 | 5.848 |
| descend_to_contact | descend | 0.00 / step_budget | (0.493, 0.106, 0.161)→(0.499, 0.098, 0.046) | (0.498, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 | 1.00 / 2.333 | 29.980 | 8.886 |
| push_to_goal | push | 1.00 / step_budget | (0.499, 0.098, 0.046)→(0.497, 0.058, 0.041) | (0.498, 0.068, 0.034)→(0.498, 0.027, 0.039) | 0.148→0.107 | 1.00 / 1.000 | 0.542 | 3.659 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.127
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.044
- phase_score: 0.257
- phase_breakdown.reach_contact_score: 0.529
- phase_breakdown.push_channel_score: 0.140

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.371
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.172
- **Median Q (composite search score)**: 0.041
- **K-run variance**: 0.0075
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.265


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.55238,"average_solve_count":105.0,"average_success_count":105.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_peg.approach_height":0.10913,"descend_to_contact.descend_backset_y":0.03169,"descend_to_contact.descend_force_threshold":9.02246,"descend_to_contact.descend_lateral_x":0.00207,"push_to_goal.push_force_threshold":33.5579,"push_to_goal.push_speed":0.03464},"optimized_scores":{"best_composite_score":0.04077,"best_fitness_score":0.37077,"best_task_score":0.17213},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":969.0,"contact_point_centroid":[0.49702,0.02295,0.00995],"force_p95":5.5808,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.66302,"mean_force":3.97247,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49045,0.06351,0.04059]},{"body_a":"attachment","body_b":"peg","contact_count":965.0,"contact_point_centroid":[0.49368,0.05153,0.04004],"force_p95":5.21965,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.26024,"mean_force":3.62358,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.4904,0.06294,0.04049]},{"body_a":"peg","body_b":"channel_base_body","contact_count":202.0,"contact_point_centroid":[0.49574,0.06383,0.00933],"force_p95":0.74866,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.58716,"phase_index":0.0,"phase_name":"approach_above_peg","phase_type":"approach","tcp_position_centroid":[0.49048,0.14817,0.2292]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_above_peg","phase_type":"approach","tcp_position_centroid":[0.4992,0.19649,0.2952]},{"body_a":"peg","body_b":"channel_base_body","contact_count":690.0,"contact_point_centroid":[0.49522,0.06381,0.0094],"force_p95":0.55034,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55295,"mean_force":0.54566,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.4866,0.09918,0.10576]}],"total_contact_groups":5},"final_pose_error":0.11578,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50122,0.00473,0.04036],"final_tcp_position":[0.49149,0.03546,0.03953],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":8.66302,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":229.0,"n_steps_budget":1000.0,"object_pos_end":[0.49518,0.06375,0.03389],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14396,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54438,"phase_name":"approach_above_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":690.0,"raw_peak_contact_force":0.55295,"subtask_id":"reach_contact","tcp_end":[0.48275,0.10393,0.17113],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14354,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":690.0,"n_steps_budget":810.0,"object_pos_end":[0.4953,0.06405,0.034],"object_pos_start":[0.49518,0.06375,0.03389],"object_to_goal_dist_end":0.14426,"object_to_goal_dist_start":0.14396,"object_z_max":0.034,"peak_contact_force":5.42082,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1934.0,"raw_peak_contact_force":8.66302,"subtask_id":"reach_contact","tcp_end":[0.49268,0.09514,0.04582],"tcp_start":[0.48275,0.10393,0.17113],"tcp_to_object_dist_end":0.03336,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50122,0.00473,0.04036],"object_pos_start":[0.4953,0.06405,0.034],"object_to_goal_dist_end":0.08474,"object_to_goal_dist_start":0.14426,"object_z_max":0.04036,"peak_contact_force":0.53926,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":230.0,"raw_peak_contact_force":2.44546,"subtask_id":"push_channel","tcp_end":[0.49149,0.03546,0.03953],"tcp_start":[0.49268,0.09514,0.04582],"tcp_to_object_dist_end":0.03225,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.78378,"average_solve_count":74.0,"average_success_count":74.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_peg.approach_height":0.08053,"descend_to_contact.descend_backset_y":0.02904,"descend_to_contact.descend_force_threshold":9.52716,"descend_to_contact.descend_lateral_x":0.00871,"push_to_goal.push_force_threshold":39.05235,"push_to_goal.push_speed":0.02444},"optimized_scores":{"best_composite_score":0.17499,"best_fitness_score":0.17166,"best_task_score":0.04392},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":624.0,"contact_point_centroid":[0.49401,0.05716,0.00941],"force_p95":0.57738,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.36779,"mean_force":0.65595,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.48226,0.09215,0.09269]},{"body_a":"attachment","body_b":"peg","contact_count":28.0,"contact_point_centroid":[0.49478,0.07658,0.05273],"force_p95":7.89788,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.18567,"mean_force":2.78862,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.49504,0.08855,0.05161]},{"body_a":"peg","body_b":"channel_base_body","contact_count":21.0,"contact_point_centroid":[0.49416,0.044,0.0098],"force_p95":5.60834,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.4614,"mean_force":1.71863,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49632,0.08735,0.04437]},{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.4953,0.07564,0.04467],"force_p95":6.43937,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.0963,"mean_force":3.50079,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49648,0.08757,0.04457]},{"body_a":"peg","body_b":"channel_base_body","contact_count":237.0,"contact_point_centroid":[0.49485,0.05907,0.00931],"force_p95":0.68087,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.60785,"phase_index":0.0,"phase_name":"approach_above_peg","phase_type":"approach","tcp_position_centroid":[0.48378,0.14452,0.2144]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_above_peg","phase_type":"approach","tcp_position_centroid":[0.49854,0.19549,0.2929]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":5.0,"contact_point_centroid":[0.47494,0.05664,0.04],"force_p95":0.2315,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25249,"mean_force":0.12539,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49581,0.08661,0.04374]}],"total_contact_groups":7},"final_pose_error":0.16636,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49279,0.05645,0.03509],"final_tcp_position":[0.49565,0.08627,0.04353],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":78.2537,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":266.0,"n_steps_budget":1000.0,"object_pos_end":[0.49406,0.05901,0.03383],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13928,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.56149,"phase_name":"approach_above_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":652.0,"raw_peak_contact_force":8.36779,"subtask_id":"reach_contact","tcp_end":[0.47022,0.09694,0.14345],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11842,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":624.0,"n_steps_budget":690.0,"object_pos_end":[0.49396,0.05817,0.03445],"object_pos_start":[0.49406,0.05901,0.03383],"object_to_goal_dist_end":0.13841,"object_to_goal_dist_start":0.13928,"object_z_max":0.03477,"peak_contact_force":78.2537,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":34.0,"raw_peak_contact_force":7.4614,"subtask_id":"reach_contact","tcp_end":[0.497,0.08801,0.04526],"tcp_start":[0.47022,0.09694,0.14345],"tcp_to_object_dist_end":0.03189,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":21.0,"n_steps_budget":1000.0,"object_pos_end":[0.49279,0.05645,0.03509],"object_pos_start":[0.49396,0.05817,0.03445],"object_to_goal_dist_end":0.13673,"object_to_goal_dist_start":0.13841,"object_z_max":0.03507,"peak_contact_force":0.54271,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":272.0,"raw_peak_contact_force":4.20518,"subtask_id":"push_channel","tcp_end":[0.49565,0.08627,0.04353],"tcp_start":[0.497,0.08801,0.04526],"tcp_to_object_dist_end":0.03112,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.54808,"average_solve_count":104.0,"average_success_count":104.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_peg.approach_height":0.10637,"descend_to_contact.descend_backset_y":0.02928,"descend_to_contact.descend_force_threshold":8.66917,"descend_to_contact.descend_lateral_x":0.00532,"push_to_goal.push_force_threshold":31.87758,"push_to_goal.push_speed":0.03355},"optimized_scores":{"best_composite_score":-0.03471,"best_fitness_score":0.29529,"best_task_score":0.08515},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":985.0,"contact_point_centroid":[0.50129,0.03874,0.00996],"force_p95":6.46276,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.53297,"mean_force":4.50218,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50371,0.07923,0.04236]},{"body_a":"attachment","body_b":"peg","contact_count":987.0,"contact_point_centroid":[0.50332,0.06735,0.04238],"force_p95":6.08374,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.28072,"mean_force":4.11904,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50369,0.07924,0.04234]},{"body_a":"peg","body_b":"channel_base_body","contact_count":528.0,"contact_point_centroid":[0.50586,0.07955,0.00939],"force_p95":0.5502,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.62444,"mean_force":0.62182,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.5168,0.11373,0.10676]},{"body_a":"attachment","body_b":"peg","contact_count":12.0,"contact_point_centroid":[0.50801,0.09842,0.05331],"force_p95":7.65431,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.60095,"mean_force":3.80226,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.50939,0.11032,0.05317]},{"body_a":"peg","body_b":"channel_base_body","contact_count":197.0,"contact_point_centroid":[0.50514,0.08085,0.00932],"force_p95":0.77424,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.6242,"phase_index":0.0,"phase_name":"approach_above_peg","phase_type":"approach","tcp_position_centroid":[0.51455,0.15542,0.22733]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_above_peg","phase_type":"approach","tcp_position_centroid":[0.50128,0.19571,0.29281]}],"total_contact_groups":6},"final_pose_error":0.13193,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50039,0.01967,0.04058],"final_tcp_position":[0.50241,0.0519,0.0412],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":10.53297,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":226.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.0809,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.02537,"phase_name":"approach_above_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":540.0,"raw_peak_contact_force":8.62444,"subtask_id":"reach_contact","tcp_end":[0.52718,0.11817,0.1687],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14157,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":528.0,"n_steps_budget":810.0,"object_pos_end":[0.50561,0.0803,0.03474],"object_pos_start":[0.50598,0.0809,0.03378],"object_to_goal_dist_end":0.16048,"object_to_goal_dist_start":0.16113,"object_z_max":0.03472,"peak_contact_force":6.2655,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1972.0,"raw_peak_contact_force":10.53297,"subtask_id":"reach_contact","tcp_end":[0.50866,0.11001,0.04802],"tcp_start":[0.52718,0.11817,0.1687],"tcp_to_object_dist_end":0.03268,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50039,0.01967,0.04058],"object_pos_start":[0.50561,0.0803,0.03474],"object_to_goal_dist_end":0.09967,"object_to_goal_dist_start":0.16048,"object_z_max":0.04058,"peak_contact_force":0.54424,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":233.0,"raw_peak_contact_force":4.32595,"subtask_id":"push_channel","tcp_end":[0.50241,0.0519,0.0412],"tcp_start":[0.50866,0.11001,0.04802],"tcp_to_object_dist_end":0.0323,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```