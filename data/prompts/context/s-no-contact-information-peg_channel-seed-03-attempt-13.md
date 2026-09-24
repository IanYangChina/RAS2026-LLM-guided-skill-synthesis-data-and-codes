## Search State

- **Seed**: 3
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | impedance_control | pose_tolerance | contact_detected | pose_tolerance | 4 | 0.3226 | 0.35 | ✅ accepted |
| 12 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | impedance_control | pose_tolerance | contact_detected | pose_tolerance | 4 | 0.3196 | 0.35 | ✅ accepted |
| 11 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | -0.1406 | 0.00 | ❌ rejected |
| 10 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | impedance_control | pose_tolerance | contact_detected | pose_tolerance | 6 | -0.1294 | 0.10 | ❌ rejected |
| 9 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | impedance_control | pose_tolerance | contact_detected | pose_tolerance | 4 | 0.2959 | 0.33 | ❌ rejected |

**Proposal policy**: task_score is 0.35 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.323) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: reach_above
  anchor: object
  offset:
  - 0.0
  - 0.05
  - 0.1
  weight: 0.3
- id: reach_goal
  metric: goal_progress
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
    entity: peg
    offset:
    - 0.0
    - 0.05
    - 0.1
    tolerance: 0.02
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
  subtask_id: reach_above
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: contact_detected
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.02
    - 0.0
    tolerance: 0.01
  parameters:
    contact_offset:
      type: scalar
      range:
      - 0.01
      - 0.03
      default: 0.02
      binds_to:
      - path: target.offset.y
        mode: replace
  guards:
  - id: contact_check
    when: after_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.01
    - 0.0
  subtask_id: reach_above
- id: push_1
  type: push
  generator: linear_cartesian
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
      distance: 0.16
      axis: channel_axis
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.03
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: reach_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.05, 0.1], tolerance=0.02
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.0], tolerance=0.01
  - parameter_bindings:
    - contact_offset: status=consumed; consumers=target.offset.y (replace)
  - guards:
    - id=contact_check, when=after_phase, predicate=contact_detected, on_failure=retry, threshold=1.0
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.01, 0.0]
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=replace_offset_projection, sign=positive}, tolerance=0.03
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)

## Design Metrics

- **Composite score**: 0.323
- **task_score** (E): 0.354
- **fitness_score**: 0.553  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_1 | 1.00 | 0.1487 |
| descend_1 | 1.00 | 0.1339 |
| push_1 | 0.67 | 0.1403 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.140, 0.167) | (0.509, 0.081, 0.040)→(0.502, 0.082, 0.034) | 0.165→0.162 |
| descend_1 | descend | 1.00 / step_budget | (0.505, 0.140, 0.167)→(0.499, 0.108, 0.039) | (0.502, 0.082, 0.034)→(0.503, 0.078, 0.034) | 0.162→0.158 |
| push_1 | push | 0.67 / step_budget | (0.499, 0.108, 0.039)→(0.498, -0.032, 0.037) | (0.503, 0.078, 0.034)→(0.503, -0.075, 0.033) | 0.158→0.012 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- terminal_score: 0.490
- phase_score: 0.644
- phase_breakdown.reach_above_score: 0.117
- phase_breakdown.reach_goal_score: 0.869

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.582
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.490
- **Median Q (composite search score)**: 0.313
- **K-run variance**: 0.0005
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.325


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91,"average_solve_count":100.0,"average_success_count":100.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09073,"descend_1.contact_offset":0.01969,"push_1.push_distance":0.15868,"push_1.push_tolerance":0.04091},"optimized_scores":{"best_composite_score":0.3024,"best_fitness_score":0.5324,"best_task_score":0.26604},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":16.0,"contact_point_centroid":[0.47493,0.09168,0.05986],"force_p95":200.23201,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":314.38405,"mean_force":145.53891,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48486,0.08734,0.05488]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":14.0,"contact_point_centroid":[0.53418,0.0816,0.05975],"force_p95":271.92272,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":277.71943,"mean_force":191.86909,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4889,0.08142,0.03699]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":189.0,"contact_point_centroid":[0.53616,0.01716,0.05997],"force_p95":197.37425,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":209.09256,"mean_force":167.24462,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49101,0.01972,0.03748]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":89.0,"contact_point_centroid":[0.47424,-0.04451,0.03816],"force_p95":62.29029,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":82.25566,"mean_force":8.8283,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49173,-0.01411,0.03749]},{"body_a":"attachment","body_b":"peg","contact_count":130.0,"contact_point_centroid":[0.49654,0.00955,0.04715],"force_p95":50.29186,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":64.73069,"mean_force":8.26177,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49102,0.02069,0.0375]},{"body_a":"peg","body_b":"channel_base_body","contact_count":140.0,"contact_point_centroid":[0.49794,-0.01526,0.00936],"force_p95":22.79214,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":56.81749,"mean_force":3.89623,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4909,0.02637,0.03749]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":44.0,"contact_point_centroid":[0.52554,-0.00362,0.02461],"force_p95":26.38423,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":41.15822,"mean_force":9.83314,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49096,0.02723,0.03762]},{"body_a":"peg","body_b":"channel_base_body","contact_count":706.0,"contact_point_centroid":[0.49476,0.05538,0.00947],"force_p95":8.45491,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.899,"mean_force":1.2151,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47722,0.09989,0.08997]},{"body_a":"attachment","body_b":"peg","contact_count":81.0,"contact_point_centroid":[0.49262,0.07211,0.05072],"force_p95":13.37814,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.8319,"mean_force":6.07883,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48733,0.08378,0.04426]},{"body_a":"peg","body_b":"link7","contact_count":18.0,"contact_point_centroid":[0.51678,0.01782,0.06995],"force_p95":13.17939,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.08903,"mean_force":3.30647,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4906,0.04465,0.03761]},{"body_a":"peg","body_b":"channel_base_body","contact_count":304.0,"contact_point_centroid":[0.49472,0.05894,0.00933],"force_p95":0.6297,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.5943,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48281,0.15731,0.2178]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49848,0.19698,0.29423]},{"body_a":"peg","body_b":"channel_base_body","contact_count":10.0,"contact_point_centroid":[0.49758,-0.10091,0.01845],"force_p95":2.21863,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.25364,"mean_force":1.3047,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49205,-0.04534,0.03725]}],"total_contact_groups":13},"final_pose_error":0.02981,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49569,-0.08123,0.04025],"final_tcp_position":[0.49205,-0.04762,0.03721],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"phases":[{"n_steps":333.0,"n_steps_budget":1000.0,"object_pos_end":[0.49412,0.05906,0.03385],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13932,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_above","tcp_end":[0.46847,0.11969,0.14746],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13131,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":712.0,"n_steps_budget":780.0,"object_pos_end":[0.49605,0.05176,0.0352],"object_pos_start":[0.49412,0.05906,0.03385],"object_to_goal_dist_end":0.1319,"object_to_goal_dist_start":0.13932,"object_z_max":0.03632,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_above","tcp_end":[0.48928,0.08138,0.0368],"tcp_start":[0.46847,0.11969,0.14746],"tcp_to_object_dist_end":0.03043,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":321.0,"n_steps_budget":990.0,"object_pos_end":[0.49569,-0.08123,0.04025],"object_pos_start":[0.49605,0.05176,0.0352],"object_to_goal_dist_end":0.00449,"object_to_goal_dist_start":0.1319,"object_z_max":0.04349,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"reach_goal","tcp_end":[0.49205,-0.04762,0.03721],"tcp_start":[0.48928,0.08138,0.0368],"tcp_to_object_dist_end":0.03394,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91262,"average_solve_count":103.0,"average_success_count":103.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09978,"descend_1.contact_offset":0.02719,"push_1.push_distance":0.1886,"push_1.push_tolerance":0.02668},"optimized_scores":{"best_composite_score":0.31306,"best_fitness_score":0.54306,"best_task_score":0.30659},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":33.0,"contact_point_centroid":[0.52512,0.11078,0.05995],"force_p95":316.83942,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":316.8699,"mean_force":291.90079,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50422,0.1107,0.04203]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":20.0,"contact_point_centroid":[0.54544,0.00022,0.06],"force_p95":154.70286,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":163.95761,"mean_force":123.2251,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50055,0.00394,0.03713]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":43.0,"contact_point_centroid":[0.52501,0.0229,0.05999],"force_p95":126.78281,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":148.82133,"mean_force":94.44805,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50108,0.02288,0.03783]},{"body_a":"peg","body_b":"channel_base_body","contact_count":138.0,"contact_point_centroid":[0.50256,-0.01645,0.00904],"force_p95":30.97715,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.90921,"mean_force":4.27639,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50108,0.02407,0.03785]},{"body_a":"attachment","body_b":"peg","contact_count":106.0,"contact_point_centroid":[0.50573,0.03601,0.04956],"force_p95":31.78086,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.88532,"mean_force":5.12645,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50125,0.04712,0.03815]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":52.0,"contact_point_centroid":[0.52525,-0.017,0.0407],"force_p95":5.76617,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.90344,"mean_force":1.17885,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50092,0.01596,0.03769]},{"body_a":"peg","body_b":"channel_base_body","contact_count":527.0,"contact_point_centroid":[0.50598,0.08046,0.00939],"force_p95":0.55009,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.35022,"mean_force":0.60442,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5145,0.1242,0.09473]},{"body_a":"peg","body_b":"channel_base_body","contact_count":281.0,"contact_point_centroid":[0.50539,0.08086,0.00934],"force_p95":0.60342,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.60106,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51425,0.1677,0.2222]},{"body_a":"attachment","body_b":"peg","contact_count":15.0,"contact_point_centroid":[0.50578,0.09874,0.04513],"force_p95":3.84067,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.92665,"mean_force":2.24219,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50434,0.11071,0.04215]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50073,0.19747,0.29393]},{"body_a":"peg","body_b":"channel_base_body","contact_count":14.0,"contact_point_centroid":[0.50532,-0.10118,0.05587],"force_p95":2.06371,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.28023,"mean_force":0.73658,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50056,-0.04477,0.03695]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":21.0,"contact_point_centroid":[0.47418,0.01569,0.02671],"force_p95":1.322,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.42416,"mean_force":0.54198,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50071,0.04826,0.03721]}],"total_contact_groups":12},"final_pose_error":0.02949,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5068,-0.07929,0.03538],"final_tcp_position":[0.50059,-0.04902,0.03694],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"phases":[{"n_steps":310.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.0809,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_above","tcp_end":[0.528,0.13954,0.15605],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13739,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":527.0,"n_steps_budget":810.0,"object_pos_end":[0.5059,0.08063,0.03413],"object_pos_start":[0.50598,0.0809,0.03378],"object_to_goal_dist_end":0.16085,"object_to_goal_dist_start":0.16113,"object_z_max":0.03431,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_above","tcp_end":[0.50392,0.11067,0.04174],"tcp_start":[0.528,0.13954,0.15605],"tcp_to_object_dist_end":0.03105,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":285.0,"n_steps_budget":1000.0,"object_pos_end":[0.5068,-0.07929,0.03538],"object_pos_start":[0.5059,0.08063,0.03413],"object_to_goal_dist_end":0.00825,"object_to_goal_dist_start":0.16085,"object_z_max":0.04803,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"reach_goal","tcp_end":[0.50059,-0.04902,0.03694],"tcp_start":[0.50392,0.11067,0.04174],"tcp_to_object_dist_end":0.03094,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91346,"average_solve_count":104.0,"average_success_count":104.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13917,"descend_1.contact_offset":0.02684,"push_1.push_distance":0.19735,"push_1.push_tolerance":0.01436},"optimized_scores":{"best_composite_score":0.35219,"best_fitness_score":0.58219,"best_task_score":0.49014},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":441.0,"contact_point_centroid":[0.54548,0.02,0.05997],"force_p95":216.23642,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":286.22268,"mean_force":156.85272,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50072,0.02336,0.03672]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":427.0,"contact_point_centroid":[0.52501,0.01773,0.05999],"force_p95":179.66059,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":235.38076,"mean_force":129.9779,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50071,0.0178,0.03678]},{"body_a":"attachment","body_b":"peg","contact_count":269.0,"contact_point_centroid":[0.50472,0.02997,0.03601],"force_p95":55.98856,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":67.67256,"mean_force":13.52257,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50076,0.04093,0.03667]},{"body_a":"peg","body_b":"channel_base_body","contact_count":542.0,"contact_point_centroid":[0.50335,-0.01234,0.00934],"force_p95":50.85465,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":67.2108,"mean_force":7.14817,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50077,0.03204,0.03671]},{"body_a":"peg","body_b":"channel_base_body","contact_count":710.0,"contact_point_centroid":[0.50576,0.10353,0.0094],"force_p95":0.57595,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.77153,"mean_force":0.59688,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50896,0.14691,0.11507]},{"body_a":"attachment","body_b":"peg","contact_count":13.0,"contact_point_centroid":[0.50515,0.12166,0.04826],"force_p95":5.49558,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.5107,"mean_force":3.1824,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50317,0.13361,0.04492]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":45.0,"contact_point_centroid":[0.52526,0.08061,0.03959],"force_p95":4.39038,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.11981,"mean_force":1.31679,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50123,0.11506,0.03617]},{"body_a":"peg","body_b":"channel_base_body","contact_count":192.0,"contact_point_centroid":[0.50503,0.10478,0.00934],"force_p95":0.71066,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.60529,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50902,0.17943,0.24279]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50055,0.19804,0.29479]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.525,0.10135,0.05901],"force_p95":0.21419,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21419,"mean_force":0.21419,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50253,0.13221,0.03753]}],"total_contact_groups":10},"final_pose_error":0.06531,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50514,-0.06316,0.02406],"final_tcp_position":[0.50065,0.00012,0.03707],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"phases":[{"n_steps":219.0,"n_steps_budget":840.0,"object_pos_end":[0.506,0.10468,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18488,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_above","tcp_end":[0.51765,0.16224,0.19617],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.17263,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":715.0,"n_steps_budget":1000.0,"object_pos_end":[0.50701,0.10146,0.03403],"object_pos_start":[0.506,0.10468,0.03384],"object_to_goal_dist_end":0.1817,"object_to_goal_dist_start":0.18488,"object_z_max":0.03544,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_above","tcp_end":[0.50251,0.13218,0.03735],"tcp_start":[0.51765,0.16224,0.19617],"tcp_to_object_dist_end":0.03122,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":637.0,"n_steps_budget":1000.0,"object_pos_end":[0.50514,-0.06316,0.02406],"object_pos_start":[0.50701,0.10146,0.03403],"object_to_goal_dist_end":0.02375,"object_to_goal_dist_start":0.1817,"object_z_max":0.04127,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"reach_goal","tcp_end":[0.50065,0.00012,0.03707],"tcp_start":[0.50251,0.13218,0.03735],"tcp_to_object_dist_end":0.06476,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```