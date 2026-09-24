## Search State

- **Seed**: 6
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → contact → push → retract | linear_cartesian | impedance_motion | impedance_motion | arc_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.4816 | 0.75 | ❌ rejected |
| 8 | approach → contact → push → retract | linear_cartesian | impedance_motion | impedance_motion | arc_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.4003 | 0.76 | ❌ rejected |
| 7 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 7 | -0.0438 | 0.00 | ❌ rejected |
| 6 | approach → contact → push → retract | linear_cartesian | impedance_motion | impedance_motion | arc_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.4852 | 0.75 | ❌ rejected |
| 5 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 9 | -0.3571 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.75 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: push_to_goal
- Frozen realised-scene SHA-256: `5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7`
- Frozen object start: [0.5045797221766332, -0.01880749562239939, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5045797221766332, -0.01880749562239939, 0.025)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.8
- Force limit: 25.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **object displacement ratio toward goal_object_position**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: push_box
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.05, 0.05, 0.05]
    mass_kg: 0.1
  - name: goal_marker
    role: target_marker
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.5046, -0.0188, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5045797221766332, -0.01880749562239939, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0046, -0.1312, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.757, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

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
| `object` | offset from object initial position (0.5045797221766332, -0.01880749562239939, 0.025) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, -0.15, 0.025) | final destination targets |
| `fixture` | offset from fixture pose (if defined, else world) | targets near fixture |

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

## Current Skill (Q=0.482) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: contact_1
  type: contact
  generator: impedance_motion
  control: force_threshold_switch
  termination: force_exceeded
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1

```

## Design Metrics

- **Composite score**: 0.482
- **task_score** (E): 0.749
- **fitness_score**: 0.642  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2889 |
| contact_1 | 1.00 | 1.00 | 0.0387 |
| push_1 | 1.00 | 1.00 | 0.1282 |
| retract_1 | 0.00 | 1.00 | 0.1287 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.103, 0.033) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / force_exceeded | (0.496, 0.103, 0.033)→(0.494, 0.066, 0.022) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.180 | 1.00 / 5.000 | 15.562 | 0.245 |
| push_1 | push | 1.00 / step_budget | (0.494, 0.066, 0.022)→(0.496, -0.061, 0.021) | (0.500, 0.029, 0.025)→(0.499, -0.099, 0.026) | 0.180→0.051 | 1.00 / 3.000 | 9.536 | 70.830 |
| retract_1 | retract | 0.00 / step_budget | (0.496, -0.061, 0.021)→(0.494, 0.036, 0.104) | (0.499, -0.099, 0.026)→(0.498, -0.099, 0.025) | 0.051→0.051 | 1.00 / 4.000 | 0.245 | 11.428 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.996
- lateral_force_integral: None
- approach_alignment: 0.546
- goal_progress: 0.996
- terminal_score: 0.996
- phase_score: 0.761
- phase_breakdown.approach_score: 0.822
- phase_breakdown.push_score: 0.735
- phase_breakdown.contact_score: 0.764

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.855
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.996
- **Median Q (composite search score)**: 0.381
- **K-run variance**: 0.0228
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Parameters at upper bound**: push_1.push_depth
- **Final σ (mean)**: 0.356


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `acf3715aaa310bcc73047d49f01e71bc863ef036ae437b7dc851a0f6d3fe40ae`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `ec1d0331416d42e6883eeb3b72499fac99c0735b785eb70ece69dc94e8044fc3`; realized-scene SHA-256: `5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50458,-0.01881,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.00458,-0.13119,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.50458,-0.01881,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.3299,"average_solve_count":194.0,"average_success_count":194.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.21119,"approach_1.speed":0.06256,"contact_1.contact_force":3.37837,"contact_1.speed":0.03691,"push_1.push_depth":0.1,"retract_1.retract_height":0.12272,"retract_1.speed":0.05281},"optimized_scores":{"best_composite_score":0.6951,"best_fitness_score":0.8551,"best_task_score":0.99585},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1106.0,"contact_point_centroid":[0.51088,-0.09931,-0.00015],"force_p95":62.02478,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":78.6918,"mean_force":22.73445,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49752,-0.04749,0.0206]},{"body_a":"attachment","body_b":"push_box","contact_count":713.0,"contact_point_centroid":[0.51209,-0.0547,0.04516],"force_p95":51.03133,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":57.12345,"mean_force":23.49214,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49761,-0.04353,0.02063]},{"body_a":"push_box","body_b":"link7","contact_count":554.0,"contact_point_centroid":[0.52491,-0.05359,0.05279],"force_p95":45.55721,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":53.70419,"mean_force":28.06503,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49795,-0.03313,0.02081]},{"body_a":"world","body_b":"push_box","contact_count":3944.0,"contact_point_centroid":[0.50011,-0.1494,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.03657,"mean_force":0.25264,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49293,-0.06569,0.05721]},{"body_a":"push_box","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.52638,-0.1368,0.0503],"force_p95":10.74653,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.68723,"mean_force":5.04121,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49606,-0.11104,0.02007]},{"body_a":"attachment","body_b":"push_box","contact_count":6.0,"contact_point_centroid":[0.51103,-0.12295,0.05067],"force_p95":3.43587,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.12963,"mean_force":1.13084,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49595,-0.11106,0.02004]},{"body_a":"world","body_b":"push_box","contact_count":3700.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49922,0.02864,0.16605]},{"body_a":"world","body_b":"push_box","contact_count":2528.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49798,0.03707,0.02531]}],"total_contact_groups":8},"final_pose_error":0.17865,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50023,-0.1495,0.02499],"final_tcp_position":[0.49377,-0.0189,0.09214],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":78.6918,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":925.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3700.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.5003,0.0578,0.03312],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07716,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":632.0,"n_steps_budget":900.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":16.57003,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2528.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49923,0.01816,0.02197],"tcp_start":[0.5003,0.0578,0.03312],"tcp_to_object_dist_end":0.03748,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":775.0,"n_steps_budget":870.0,"object_pos_end":[0.50149,-0.14786,0.02565],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.00269,"object_to_goal_dist_start":0.13127,"object_z_max":0.0287,"peak_contact_force":13.32604,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2373.0,"raw_peak_contact_force":78.6918,"tcp_end":[0.49608,-0.11096,0.02008],"tcp_start":[0.49923,0.01816,0.02197],"tcp_to_object_dist_end":0.03771,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50023,-0.1495,0.02499],"object_pos_start":[0.50149,-0.14786,0.02565],"object_to_goal_dist_end":0.00054,"object_to_goal_dist_start":0.00269,"object_z_max":0.02566,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3953.0,"raw_peak_contact_force":13.03657,"tcp_end":[0.49377,-0.0189,0.09214],"tcp_start":[0.49608,-0.11096,0.02008],"tcp_to_object_dist_end":0.147,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `589e611c6c27578474525e3fd29be4fb5907d8bbd5d1ca44922bfd811e342c78`; realized-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51501,0.04767,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.01501,-0.19767,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.51501,0.04767,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.77215,"average_solve_count":158.0,"average_success_count":158.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.18655,"approach_1.speed":0.09077,"contact_1.contact_force":8.09896,"contact_1.speed":0.03645,"push_1.push_depth":0.09698,"retract_1.retract_height":0.12656,"retract_1.speed":0.09843},"optimized_scores":{"best_composite_score":0.38119,"best_fitness_score":0.54119,"best_task_score":0.62908},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1143.0,"contact_point_centroid":[0.52147,-0.03477,-0.00015],"force_p95":59.34647,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":74.38284,"mean_force":31.65212,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50351,0.02052,0.02156]},{"body_a":"push_box","body_b":"link7","contact_count":724.0,"contact_point_centroid":[0.52977,0.00204,0.05402],"force_p95":50.61609,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":62.29456,"mean_force":33.99347,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50343,0.02138,0.02141]},{"body_a":"attachment","body_b":"push_box","contact_count":744.0,"contact_point_centroid":[0.52089,0.01253,0.04959],"force_p95":51.8263,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":60.95785,"mean_force":32.64106,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50358,0.02305,0.02139]},{"body_a":"world","body_b":"push_box","contact_count":3872.0,"contact_point_centroid":[0.50013,-0.07682,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.44135,"mean_force":0.25956,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49513,0.02096,0.07943]},{"body_a":"push_box","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.52253,-0.06347,0.05459],"force_p95":18.65625,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.13554,"mean_force":11.13978,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49809,-0.04,0.0216]},{"body_a":"attachment","body_b":"push_box","contact_count":26.0,"contact_point_centroid":[0.51561,-0.04913,0.05274],"force_p95":8.52379,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.55633,"mean_force":2.03114,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49682,-0.03814,0.02324]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50421,0.06059,0.16418]},{"body_a":"world","body_b":"push_box","contact_count":2356.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50809,0.10189,0.02402]}],"total_contact_groups":8},"final_pose_error":0.0684,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50019,-0.07647,0.02499],"final_tcp_position":[0.49603,0.0866,0.12463],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":74.38284,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.51028,0.12138,0.03128],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07413,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":589.0,"n_steps_budget":870.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":19.29704,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2356.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.50942,0.08463,0.02141],"tcp_start":[0.51028,0.12138,0.03128],"tcp_to_object_dist_end":0.03756,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":746.0,"n_steps_budget":840.0,"object_pos_end":[0.50117,-0.07828,0.02856],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.07181,"object_to_goal_dist_start":0.19823,"object_z_max":0.02912,"peak_contact_force":14.50894,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2611.0,"raw_peak_contact_force":74.38284,"tcp_end":[0.49818,-0.03987,0.02163],"tcp_start":[0.50942,0.08463,0.02141],"tcp_to_object_dist_end":0.03915,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50019,-0.07647,0.02499],"object_pos_start":[0.50117,-0.07828,0.02856],"object_to_goal_dist_end":0.07353,"object_to_goal_dist_start":0.07181,"object_z_max":0.02856,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3902.0,"raw_peak_contact_force":20.44135,"tcp_end":[0.49603,0.0866,0.12463],"tcp_start":[0.49818,-0.03987,0.02163],"tcp_to_object_dist_end":0.19115,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f2c9c63f0d9eca1b3ff8bf951759f6a3adee73f9f65e1cd3613c5e9d1203ebcc`; realized-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47924,0.05847,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02076,-0.20847,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47924,0.05847,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.49462,"average_solve_count":186.0,"average_success_count":186.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.24483,"approach_1.speed":0.08437,"contact_1.contact_force":13.40677,"contact_1.speed":0.0389,"push_1.push_depth":0.0988,"retract_1.retract_height":0.1781,"retract_1.speed":0.01917},"optimized_scores":{"best_composite_score":0.36855,"best_fitness_score":0.52855,"best_task_score":0.62285},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1090.0,"contact_point_centroid":[0.49331,-0.02014,-8e-05],"force_p95":44.98871,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":59.41491,"mean_force":11.88067,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48434,0.02592,0.02031]},{"body_a":"attachment","body_b":"push_box","contact_count":698.0,"contact_point_centroid":[0.49216,0.02067,0.03442],"force_p95":38.22983,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.50604,"mean_force":13.51081,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48341,0.03204,0.02043]},{"body_a":"push_box","body_b":"link7","contact_count":278.0,"contact_point_centroid":[0.5072,0.04096,0.05182],"force_p95":31.22945,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.0814,"mean_force":20.90826,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47842,0.06367,0.02092]},{"body_a":"world","body_b":"push_box","contact_count":3992.0,"contact_point_centroid":[0.49446,-0.07118,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.80534,"mean_force":0.24592,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49187,0.00197,0.05884]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.49438,-0.04544,0.02029],"force_p95":0.63867,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.66349,"mean_force":0.41528,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49459,-0.03348,0.02012]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48727,0.06509,0.16572]},{"body_a":"world","body_b":"push_box","contact_count":2068.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4737,0.11189,0.02653]}],"total_contact_groups":7},"final_pose_error":0.12184,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49446,-0.07118,0.02499],"final_tcp_position":[0.49315,0.04117,0.09563],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":59.41491,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.47644,0.13039,0.03438],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07258,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":517.0,"n_steps_budget":780.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":10.81914,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2068.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.47431,0.09542,0.02289],"tcp_start":[0.47644,0.13039,0.03438],"tcp_to_object_dist_end":0.03733,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":765.0,"n_steps_budget":870.0,"object_pos_end":[0.49453,-0.07035,0.02502],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.07983,"object_to_goal_dist_start":0.2095,"object_z_max":0.03155,"peak_contact_force":0.77411,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2066.0,"raw_peak_contact_force":59.41491,"tcp_end":[0.49459,-0.03343,0.02013],"tcp_start":[0.47431,0.09542,0.02289],"tcp_to_object_dist_end":0.03724,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49446,-0.07118,0.02499],"object_pos_start":[0.49453,-0.07035,0.02502],"object_to_goal_dist_end":0.07901,"object_to_goal_dist_start":0.07983,"object_z_max":0.02502,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3994.0,"raw_peak_contact_force":0.80534,"tcp_end":[0.49315,0.04117,0.09563],"tcp_start":[0.49459,-0.03343,0.02013],"tcp_to_object_dist_end":0.13272,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```