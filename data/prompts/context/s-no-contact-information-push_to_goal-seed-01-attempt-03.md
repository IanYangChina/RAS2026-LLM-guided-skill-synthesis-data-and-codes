## Search State

- **Seed**: 1
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 5 | -0.0420 | 0.01 | ❌ rejected |
| 2 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 3 | 0.1523 | 0.00 | ❌ rejected |
| 1 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 2 | 0.0096 | 0.00 | ❌ rejected |
| 0 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.2056 | 0.54 | ✅ accepted |

**Proposal policy**: task_score is 0.01 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `258b33ff0697721ed1ba4810cf28d81707440dffd73b12c632f307c6591915c0`
- Frozen object start: [0.5014185949640309, 0.05405564355911223, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5014185949640309, 0.05405564355911223, 0.025)
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
  frozen_object_start: [0.5014, 0.0541, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5014185949640309, 0.05405564355911223, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0014, -0.2041, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 258b33ff0697721ed1ba4810cf28d81707440dffd73b12c632f307c6591915c0

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
| `object` | offset from object initial position (0.5014185949640309, 0.05405564355911223, 0.025) | approach/contact targets near object start |
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

## Current Skill (Q=-0.042) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: rotate_1
  type: rotate
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
- id: align_2
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01

```

## Design Metrics

- **Composite score**: -0.042
- **task_score** (E): 0.011
- **fitness_score**: 0.098  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.340

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_1 | 1.00 | 0.1786 |
| descend_1 | 1.00 | 0.0803 |
| contact_1 | 1.00 | 0.0002 |
| push_1 | 0.00 | 0.0001 |
| retract_1 | 0.67 | 0.1620 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.472, -0.001, 0.129) | (0.474, -0.001, 0.025)→(0.474, -0.001, 0.025) | 0.154→0.154 |
| descend_1 | descend | 1.00 / step_budget | (0.472, -0.001, 0.129)→(0.471, 0.022, 0.052) | (0.474, -0.001, 0.025)→(0.474, -0.001, 0.025) | 0.154→0.154 |
| contact_1 | contact | 1.00 / force_exceeded | (0.471, 0.022, 0.052)→(0.470, 0.022, 0.052) | (0.474, -0.001, 0.025)→(0.474, -0.001, 0.025) | 0.154→0.154 |
| push_1 | push | 0.00 / guard_failure | (0.470, 0.022, 0.052)→(0.470, 0.022, 0.052) | (0.474, -0.001, 0.025)→(0.474, -0.001, 0.025) | 0.154→0.154 |
| retract_1 | retract | 0.67 / step_budget | (0.470, 0.022, 0.052)→(0.495, -0.124, 0.111) | (0.474, -0.001, 0.025)→(0.474, -0.002, 0.025) | 0.154→0.152 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.013
- approach_alignment: 0.798
- goal_progress: 0.013
- terminal_score: 0.013
- phase_score: 0.156
- phase_breakdown.push_to_goal_score: 0.000
- phase_breakdown.reach_object_score: 0.520

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.099
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.013
- **Median Q (composite search score)**: -0.042
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.324


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `f21cc79f03d9e871b86947069440973ee7e2ef557ebaac0b26b4f6cbdabf5bb1`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `ec03d65db90cc6b4602194a1eefa4c3104517a971e566e099fb50a3df7102251`; realized-scene SHA-256: `258b33ff0697721ed1ba4810cf28d81707440dffd73b12c632f307c6591915c0`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50142,0.05406,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.00142,-0.20406,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.50142,0.05406,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.76667,"average_solve_count":90.0,"average_success_count":90.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.13141,"contact_1.contact_force_threshold":12.29427,"push_1.force_limit_guard":21.23583,"push_1.push_distance":0.19061,"push_1.push_speed":0.07133},"optimized_scores":{"best_composite_score":-0.04198,"best_fitness_score":0.09802,"best_task_score":0.01094},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.50928,0.07621,0.04942],"force_p95":45.9821,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.9821,"mean_force":45.9821,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49754,0.07634,0.0515]},{"body_a":"attachment","body_b":"push_box","contact_count":46.0,"contact_point_centroid":[0.50871,0.07349,0.04972],"force_p95":43.70445,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.32566,"mean_force":30.86022,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49698,0.0732,0.05199]},{"body_a":"world","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.50977,0.0624,-6e-05],"force_p95":40.27749,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":44.55094,"mean_force":15.45578,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49754,0.07634,0.0515]},{"body_a":"attachment","body_b":"push_box","contact_count":9.0,"contact_point_centroid":[0.50912,0.07615,0.04969],"force_p95":38.87163,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.56646,"mean_force":30.99052,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49738,0.07611,0.05194]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.50925,0.07624,0.04936],"force_p95":35.3921,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.59846,"mean_force":31.97042,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49751,0.07638,0.0514]},{"body_a":"world","body_b":"push_box","contact_count":1925.0,"contact_point_centroid":[0.50151,0.05415,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.37181,"mean_force":0.39127,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49641,0.06365,0.08793]},{"body_a":"world","body_b":"push_box","contact_count":3946.0,"contact_point_centroid":[0.5009,0.05157,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.24013,"mean_force":0.60704,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49501,-0.00787,0.0744]},{"body_a":"world","body_b":"push_box","contact_count":8.0,"contact_point_centroid":[0.50764,0.06658,-7e-05],"force_p95":20.74841,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.82594,"mean_force":12.40004,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49751,0.07638,0.05141]},{"body_a":"world","body_b":"push_box","contact_count":3276.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49812,0.02505,0.21423]}],"total_contact_groups":9},"final_pose_error":0.06898,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50096,0.05183,0.02499],"final_tcp_position":[0.49582,-0.08603,0.09954],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"phases":[{"n_steps":819.0,"n_steps_budget":870.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.49807,0.05113,0.12863],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10374,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":483.0,"n_steps_budget":600.0,"object_pos_end":[0.5015,0.05417,0.02494],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.20418,"object_to_goal_dist_start":0.20406,"object_z_max":0.02499,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.49754,0.07634,0.0515],"tcp_start":[0.49807,0.05113,0.12863],"tcp_to_object_dist_end":0.03482,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50147,0.05419,0.02493],"object_pos_start":[0.5015,0.05417,0.02494],"object_to_goal_dist_end":0.20419,"object_to_goal_dist_start":0.20418,"object_z_max":0.02494,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","subtask_id":"reach_object","tcp_end":[0.49753,0.07636,0.05145],"tcp_start":[0.49754,0.07634,0.0515],"tcp_to_object_dist_end":0.03479,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50143,0.0542,0.02492],"object_pos_start":[0.50147,0.05419,0.02493],"object_to_goal_dist_end":0.2042,"object_to_goal_dist_start":0.20419,"object_z_max":0.02493,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_to_goal","tcp_end":[0.49747,0.0764,0.05132],"tcp_start":[0.49749,0.07639,0.05136],"tcp_to_object_dist_end":0.03472,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50096,0.05183,0.02499],"object_pos_start":[0.50137,0.0542,0.02489],"object_to_goal_dist_end":0.20183,"object_to_goal_dist_start":0.2042,"object_z_max":0.02501,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.49582,-0.08603,0.09954],"tcp_start":[0.49747,0.0764,0.05132],"tcp_to_object_dist_end":0.1568,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `060d405a872aae8d4597ed6284dedb60e9c99f80071c0520b1a8a2986f3c114d`; realized-scene SHA-256: `8c36a5f9300ba3a57ccc09620ec8ba0a5276276ed83fb4303679e150911bfa14`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47139,-0.02418,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02861,-0.12582,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47139,-0.02418,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.74227,"average_solve_count":97.0,"average_success_count":97.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.10873,"contact_1.contact_force_threshold":8.13586,"push_1.force_limit_guard":24.98386,"push_1.push_distance":0.06314,"push_1.push_speed":0.06571},"optimized_scores":{"best_composite_score":-0.04129,"best_fitness_score":0.09871,"best_task_score":0.01271},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.47927,-0.00119,0.04991],"force_p95":31.4727,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.64562,"mean_force":20.91642,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46753,-0.00116,0.05231]},{"body_a":"attachment","body_b":"push_box","contact_count":7.0,"contact_point_centroid":[0.47906,-0.0012,0.04973],"force_p95":30.22959,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.35907,"mean_force":20.2271,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46733,-0.00115,0.05197]},{"body_a":"attachment","body_b":"push_box","contact_count":36.0,"contact_point_centroid":[0.47885,-0.00332,0.05],"force_p95":27.61724,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.49244,"mean_force":19.78463,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.46713,-0.00366,0.05233]},{"body_a":"world","body_b":"push_box","contact_count":6.0,"contact_point_centroid":[0.46306,-0.02418,-1e-05],"force_p95":21.16077,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.53166,"mean_force":7.25946,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46754,-0.00117,0.05233]},{"body_a":"world","body_b":"push_box","contact_count":3784.0,"contact_point_centroid":[0.47159,-0.02624,-1e-05],"force_p95":0.24543,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.87959,"mean_force":0.436,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48016,-0.07461,0.08379]},{"body_a":"world","body_b":"push_box","contact_count":20.0,"contact_point_centroid":[0.4613,-0.02418,-2e-05],"force_p95":11.25383,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.69905,"mean_force":7.3663,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46731,-0.00117,0.05193]},{"body_a":"world","body_b":"push_box","contact_count":3140.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48408,-0.01133,0.21388]},{"body_a":"world","body_b":"push_box","contact_count":1804.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4674,-0.01212,0.08956]}],"total_contact_groups":8},"final_pose_error":0.01134,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47158,-0.02582,0.02499],"final_tcp_position":[0.49532,-0.14336,0.11709],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"phases":[{"n_steps":785.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.46966,-0.02291,0.12938],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10441,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":451.0,"n_steps_budget":600.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.46755,-0.00118,0.05236],"tcp_start":[0.46966,-0.02291,0.12938],"tcp_to_object_dist_end":0.03596,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":2.0,"n_steps_budget":600.0,"object_pos_end":[0.47132,-0.02417,0.02503],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12906,"object_to_goal_dist_start":0.12903,"object_z_max":0.02501,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","subtask_id":"reach_object","tcp_end":[0.46744,-0.00112,0.05218],"tcp_start":[0.46755,-0.00118,0.05236],"tcp_to_object_dist_end":0.03582,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":7.0,"n_steps_budget":600.0,"object_pos_end":[0.4713,-0.02416,0.02493],"object_pos_start":[0.47132,-0.02417,0.02503],"object_to_goal_dist_end":0.12907,"object_to_goal_dist_start":0.12906,"object_z_max":0.02504,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_to_goal","tcp_end":[0.46723,-0.00126,0.05174],"tcp_start":[0.46725,-0.00124,0.05179],"tcp_to_object_dist_end":0.03549,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":963.0,"n_steps_budget":1000.0,"object_pos_end":[0.47158,-0.02582,0.02499],"object_pos_start":[0.47131,-0.02417,0.02488],"object_to_goal_dist_end":0.12739,"object_to_goal_dist_start":0.12906,"object_z_max":0.02527,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.49532,-0.14336,0.11709],"tcp_start":[0.46723,-0.00126,0.05174],"tcp_to_object_dist_end":0.1512,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `c4af277909bfbef2010e50829d2192ea184fe34d7420833f45dd73455a81c9b6`; realized-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45028,-0.03158,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.04972,-0.11842,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.45028,-0.03158,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.73786,"average_solve_count":103.0,"average_success_count":103.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.0945,"contact_1.contact_force_threshold":11.25538,"push_1.force_limit_guard":17.37538,"push_1.push_distance":0.22909,"push_1.push_speed":0.12588},"optimized_scores":{"best_composite_score":-0.04278,"best_fitness_score":0.09722,"best_task_score":0.00842},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.45805,-0.00848,0.0499],"force_p95":31.45842,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.35498,"mean_force":17.92408,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.44631,-0.00843,0.05231]},{"body_a":"world","body_b":"push_box","contact_count":16.0,"contact_point_centroid":[0.45028,-0.03159,-1e-05],"force_p95":11.42145,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.71945,"mean_force":4.72428,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.44631,-0.00843,0.05231]},{"body_a":"attachment","body_b":"push_box","contact_count":26.0,"contact_point_centroid":[0.45797,-0.00982,0.05004],"force_p95":21.05048,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.37965,"mean_force":15.7975,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.44624,-0.01001,0.05243]},{"body_a":"world","body_b":"push_box","contact_count":3794.0,"contact_point_centroid":[0.45059,-0.03298,-1e-05],"force_p95":0.24534,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.60252,"mean_force":0.35578,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.46951,-0.07806,0.08405]},{"body_a":"world","body_b":"push_box","contact_count":3248.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47411,-0.0148,0.21393]},{"body_a":"world","body_b":"push_box","contact_count":1816.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.44698,-0.01928,0.09002]},{"body_a":"world","body_b":"push_box","contact_count":12.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44659,-0.00847,0.05262]}],"total_contact_groups":7},"final_pose_error":0.01152,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.4506,-0.03262,0.02499],"final_tcp_position":[0.49451,-0.14363,0.11713],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"phases":[{"n_steps":812.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.44959,-0.02993,0.12952],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10455,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":454.0,"n_steps_budget":600.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object","tcp_end":[0.44667,-0.00849,0.05273],"tcp_start":[0.44959,-0.02993,0.12952],"tcp_to_object_dist_end":0.03627,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":3.0,"n_steps_budget":600.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","subtask_id":"reach_object","tcp_end":[0.4464,-0.00843,0.05243],"tcp_start":[0.44667,-0.00849,0.05273],"tcp_to_object_dist_end":0.03611,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.45029,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_to_goal","tcp_end":[0.44618,-0.00844,0.05214],"tcp_start":[0.44623,-0.00844,0.0522],"tcp_to_object_dist_end":0.03591,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":963.0,"n_steps_budget":1000.0,"object_pos_end":[0.4506,-0.03262,0.02499],"object_pos_start":[0.45029,-0.03158,0.02498],"object_to_goal_dist_end":0.12735,"object_to_goal_dist_start":0.12843,"object_z_max":0.02525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.49451,-0.14363,0.11713],"tcp_start":[0.44618,-0.00844,0.05214],"tcp_to_object_dist_end":0.1508,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```