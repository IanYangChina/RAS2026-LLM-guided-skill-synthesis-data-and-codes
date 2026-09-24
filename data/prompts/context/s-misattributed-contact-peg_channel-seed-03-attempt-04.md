## Search State

- **Seed**: 3
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.2701 | 0.12 | ✅ accepted |
| 3 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.1557 | 0.00 | ❌ rejected |
| 2 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | force_exceeded | time_limit | 3 | -0.0678 | 0.03 | ❌ rejected |
| 1 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.1474 | 0.04 | ❌ rejected |
| 0 | rotate → retract → descend → pull | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | -0.1168 | 0.09 | ✅ accepted |

**Proposal policy**: task_score is 0.12 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`
- Frozen object start: [0.46685193337148995, 0.058944840527687975, 0.04]
- Frozen task target: [0.46685193337148995, -0.10105515947231203, 0.04]
- Goal object position: (0.46685193337148995, -0.10105515947231203, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.46685193337148995, 0.058944840527687975, 0.04)
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
  frozen_object_start: [0.4669, 0.0589, 0.04]
  frozen_task_target: [0.4669, -0.1011, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.46685193337148995, 0.058944840527687975, 0.04]}
  frozen_targets: {'channel_exit': [0.46685193337148995, -0.10105515947231203, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834

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
| `object` | offset from object initial position (0.46685193337148995, 0.058944840527687975, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.46685193337148995, -0.10105515947231203, 0.04) | final destination targets |
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

## Current Skill (Q=0.270) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: approach_peg
  anchor: object
  offset:
  - 0.0
  - 0.04
  - 0.1
  weight: 0.2
- id: contact_peg
  anchor: object
  offset:
  - 0.0
  - 0.04
  - 0.02
  weight: 0.3
- id: insert_peg
  offset:
  - 0.0
  - 0.0
  - 0.02
  weight: 0.5
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
    - 0.04
    - 0.1
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
  subtask_id: approach_peg
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.04
    - 0.02
    orientation:
      mode: none
  parameters:
    descend_force_threshold:
      type: scalar
      range:
      - 1.0
      - 15.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  subtask_id: contact_peg
- id: push_1
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
    - 0.02
    tolerance: 0.01
    orientation:
      mode: none
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    push_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  guards:
  - id: force_guard
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: abort
  subtask_id: insert_peg

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.04, 0.1], tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.04, 0.02]
  - orientation: mode=none
  - parameter_bindings:
    - descend_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.02], tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=abort, threshold=40.0

## Design Metrics

- **Composite score**: 0.270
- **task_score** (E): 0.119
- **fitness_score**: 0.500  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1727 |
| descend_1 | 0.00 | 1.00 | 0.0925 |
| push_1 | 1.00 | 1.00 | 0.1931 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.127, 0.147) | (0.509, 0.081, 0.040)→(0.502, 0.081, 0.034) | 0.165→0.162 | 1.00 / 1.000 | 0.545 | 0.560 |
| descend_1 | descend | 0.00 / step_budget | (0.505, 0.127, 0.147)→(0.499, 0.121, 0.057) | (0.502, 0.081, 0.034)→(0.502, 0.082, 0.034) | 0.162→0.162 | 1.00 / 1.000 | 0.584 | 20.579 |
| push_1 | push | 1.00 / step_budget | (0.499, 0.121, 0.057)→(0.496, -0.072, 0.055) | (0.502, 0.082, 0.034)→(0.501, 0.031, 0.024) | 0.162→0.112 | 1.00 / 1.000 | 0.540 | 3.954 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.324
- alignment_error: None
- force_efficiency: 0.465
- terminal_score: 0.171
- phase_score: 0.759
- phase_breakdown.contact_peg_score: 0.655
- phase_breakdown.insert_peg_score: 0.798
- phase_breakdown.approach_peg_score: 0.819

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.524
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.171
- **Median Q (composite search score)**: 0.271
- **K-run variance**: 0.0004
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.244


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `cc7283febf3c95cef1fde4c5a16cbcb134186cb6faf3a169717a9aa53375931d`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `178d67757a065da6e29d31070e25f6065dc7e42bdbf58dfbff0deec513214033`; realized-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46685,0.05894,0.04]},{"name":"goal","value":[0.46685,-0.10106,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,0.05894,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.46685,-0.10106,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.12987,"average_solve_count":77.0,"average_success_count":77.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.31417,"descend_1.descend_force_threshold":7.95163,"push_1.push_speed":0.1028,"push_1.push_tolerance":0.00886},"optimized_scores":{"best_composite_score":0.27134,"best_fitness_score":0.50134,"best_task_score":0.10281},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":909.0,"contact_point_centroid":[0.49435,0.01998,0.00867],"force_p95":12.9967,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.52277,"mean_force":3.07434,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49052,0.00987,0.0532]},{"body_a":"attachment","body_b":"peg","contact_count":237.0,"contact_point_centroid":[0.49293,0.04941,0.05025],"force_p95":13.9092,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.18431,"mean_force":9.41021,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48758,0.05955,0.05225]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":19.0,"contact_point_centroid":[0.47499,0.03387,0.02441],"force_p95":8.91616,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.26519,"mean_force":3.377,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49341,-0.03963,0.05408]},{"body_a":"peg","body_b":"channel_base_body","contact_count":460.0,"contact_point_centroid":[0.49434,0.05891,0.00935],"force_p95":0.59084,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.578,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48176,0.15049,0.21849]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49858,0.19714,0.29524]},{"body_a":"peg","body_b":"channel_base_body","contact_count":567.0,"contact_point_centroid":[0.49424,0.05891,0.00939],"force_p95":0.55028,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.54602,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47601,0.10187,0.09986]}],"total_contact_groups":6},"final_pose_error":0.0099,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49365,0.01003,0.02415],"final_tcp_position":[0.49555,-0.07278,0.05489],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":15.52277,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":489.0,"n_steps_budget":600.0,"object_pos_end":[0.4942,0.05887,0.03386],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13913,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54464,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":567.0,"raw_peak_contact_force":0.55382,"subtask_id":"approach_peg","tcp_end":[0.46637,0.10571,0.14731],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12585,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":567.0,"n_steps_budget":630.0,"object_pos_end":[0.49428,0.05908,0.03393],"object_pos_start":[0.4942,0.05887,0.03386],"object_to_goal_dist_end":0.13933,"object_to_goal_dist_start":0.13913,"object_z_max":0.03393,"peak_contact_force":0.62534,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1165.0,"raw_peak_contact_force":15.52277,"subtask_id":"contact_peg","tcp_end":[0.48837,0.09855,0.05526],"tcp_start":[0.46637,0.10571,0.14731],"tcp_to_object_dist_end":0.04525,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":910.0,"n_steps_budget":1000.0,"object_pos_end":[0.49365,0.01003,0.02415],"object_pos_start":[0.49428,0.05908,0.03393],"object_to_goal_dist_end":0.09164,"object_to_goal_dist_start":0.13933,"object_z_max":0.0404,"peak_contact_force":0.54362,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":495.0,"raw_peak_contact_force":4.20518,"subtask_id":"insert_peg","tcp_end":[0.49555,-0.07278,0.05489],"tcp_start":[0.48837,0.09855,0.05526],"tcp_to_object_dist_end":0.08835,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1ee374347cb6f80436633ebcb956aaa73ea8a10685d65b21d5c3814cf0c53498`; realized-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53544,0.08091,0.04]},{"name":"goal","value":[0.53544,-0.07909,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.08091,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53544,-0.07909,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.12658,"average_solve_count":79.0,"average_success_count":79.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.38231,"descend_1.descend_force_threshold":3.9707,"push_1.push_speed":0.11129,"push_1.push_tolerance":0.01194},"optimized_scores":{"best_composite_score":0.24475,"best_fitness_score":0.47475,"best_task_score":0.08306},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":228.0,"contact_point_centroid":[0.50461,0.0727,0.05259],"force_p95":16.10428,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.4887,"mean_force":8.69366,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50023,0.08345,0.05436]},{"body_a":"peg","body_b":"channel_base_body","contact_count":977.0,"contact_point_centroid":[0.50508,0.03961,0.0086],"force_p95":10.73922,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.12677,"mean_force":2.45168,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49859,0.02145,0.05459]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":33.0,"contact_point_centroid":[0.52501,0.06894,0.05533],"force_p95":8.65795,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.35302,"mean_force":6.88405,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50062,0.09693,0.05436]},{"body_a":"peg","body_b":"channel_base_body","contact_count":461.0,"contact_point_centroid":[0.50562,0.08086,0.00935],"force_p95":0.56049,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.57986,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51474,0.16102,0.21794]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50034,0.19767,0.29506]},{"body_a":"peg","body_b":"channel_base_body","contact_count":371.0,"contact_point_centroid":[0.50602,0.08085,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55008,"mean_force":0.54677,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51644,0.12299,0.10203]}],"total_contact_groups":6},"final_pose_error":0.00993,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50343,0.02961,0.02413],"final_tcp_position":[0.49617,-0.07233,0.05499],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":19.4887,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":490.0,"n_steps_budget":600.0,"object_pos_end":[0.50598,0.0809,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.5464,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":371.0,"raw_peak_contact_force":0.55008,"subtask_id":"approach_peg","tcp_end":[0.52968,0.12592,0.1462],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12341,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":371.0,"n_steps_budget":630.0,"object_pos_end":[0.50596,0.08089,0.03378],"object_pos_start":[0.50598,0.0809,0.03378],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16113,"object_z_max":0.03378,"peak_contact_force":0.60162,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1238.0,"raw_peak_contact_force":19.4887,"subtask_id":"contact_peg","tcp_end":[0.50457,0.12052,0.05845],"tcp_start":[0.52968,0.12592,0.1462],"tcp_to_object_dist_end":0.04671,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":980.0,"n_steps_budget":1000.0,"object_pos_end":[0.50343,0.02961,0.02413],"object_pos_start":[0.50596,0.08089,0.03378],"object_to_goal_dist_end":0.1108,"object_to_goal_dist_start":0.16112,"object_z_max":0.04043,"peak_contact_force":0.5453,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":497.0,"raw_peak_contact_force":4.32595,"subtask_id":"insert_peg","tcp_end":[0.49617,-0.07233,0.05499],"tcp_start":[0.50457,0.12052,0.05845],"tcp_to_object_dist_end":0.10675,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e082b57d1be6744ae6d3993c25b90215f3fc56dc7131af62e0630c4f325e4b04`; realized-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5244,0.10464,0.04]},{"name":"goal","value":[0.5244,-0.05536,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.10464,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.5244,-0.05536,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.13514,"average_solve_count":74.0,"average_success_count":74.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.38001,"descend_1.descend_force_threshold":9.14658,"push_1.push_speed":0.13713,"push_1.push_tolerance":0.01168},"optimized_scores":{"best_composite_score":0.29418,"best_fitness_score":0.52418,"best_task_score":0.17142},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":217.0,"contact_point_centroid":[0.50411,0.09563,0.05232],"force_p95":19.6331,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.72636,"mean_force":12.6291,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49935,0.10613,0.05413]},{"body_a":"peg","body_b":"channel_base_body","contact_count":946.0,"contact_point_centroid":[0.5063,0.06249,0.00856],"force_p95":15.84117,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.88655,"mean_force":3.20351,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49806,0.03616,0.05439]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":96.0,"contact_point_centroid":[0.52506,0.08886,0.04232],"force_p95":10.06158,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.06138,"mean_force":7.04682,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49932,0.10806,0.05405]},{"body_a":"peg","body_b":"channel_base_body","contact_count":424.0,"contact_point_centroid":[0.50545,0.10464,0.00937],"force_p95":0.57956,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.57297,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50928,0.17284,0.21927]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50005,0.19842,0.29568]},{"body_a":"peg","body_b":"channel_base_body","contact_count":388.0,"contact_point_centroid":[0.50595,0.10457,0.00939],"force_p95":0.57564,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57724,"mean_force":0.54638,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5104,0.14585,0.10225]}],"total_contact_groups":6},"final_pose_error":0.01129,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50665,0.05275,0.02405],"final_tcp_position":[0.49617,-0.07065,0.05497],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":26.72636,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":451.0,"n_steps_budget":600.0,"object_pos_end":[0.50594,0.10472,0.03383],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18492,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54315,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":388.0,"raw_peak_contact_force":0.57724,"subtask_id":"approach_peg","tcp_end":[0.51933,0.14831,0.14777],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12272,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":388.0,"n_steps_budget":600.0,"object_pos_end":[0.50585,0.1047,0.03384],"object_pos_start":[0.50594,0.10472,0.03383],"object_to_goal_dist_end":0.18489,"object_to_goal_dist_start":0.18492,"object_z_max":0.03384,"peak_contact_force":0.52456,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1259.0,"raw_peak_contact_force":26.72636,"subtask_id":"contact_peg","tcp_end":[0.50336,0.14401,0.05804],"tcp_start":[0.51933,0.14831,0.14777],"tcp_to_object_dist_end":0.04623,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":950.0,"n_steps_budget":1000.0,"object_pos_end":[0.50665,0.05275,0.02405],"object_pos_start":[0.50585,0.1047,0.03384],"object_to_goal_dist_end":0.13387,"object_to_goal_dist_start":0.18489,"object_z_max":0.04027,"peak_contact_force":0.53144,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":456.0,"raw_peak_contact_force":3.33087,"subtask_id":"insert_peg","tcp_end":[0.49617,-0.07065,0.05497],"tcp_start":[0.50336,0.14401,0.05804],"tcp_to_object_dist_end":0.12764,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```