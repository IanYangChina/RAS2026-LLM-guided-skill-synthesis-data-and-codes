## Search State

- **Seed**: 0
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.3238 | 0.42 | ❌ rejected |
| 10 | approach → contact → push → retract | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | force_threshold_switch | admittance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | -0.1144 | 0.00 | ❌ rejected |
| 9 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.5205 | 0.39 | ❌ rejected |
| 8 | approach → contact → push → retract | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | force_threshold_switch | admittance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.7875 | 0.88 | ❌ rejected |
| 7 | approach → contact → push → retract | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | force_threshold_switch | admittance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | time_limit | 5 | 0.6056 | 0.35 | ❌ rejected |

**Proposal policy**: task_score is 0.42 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `79fe20ee7316d80bc617c84166fccacf882b4f96b2faf4b155be83e4f318b183`
- Frozen object start: [0.5164354024785746, -0.027625594348335558, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5164354024785746, -0.027625594348335558, 0.025)
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
  frozen_object_start: [0.5164, -0.0276, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5164354024785746, -0.027625594348335558, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0164, -0.1224, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 79fe20ee7316d80bc617c84166fccacf882b4f96b2faf4b155be83e4f318b183

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.915, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.5164354024785746, -0.027625594348335558, 0.025) | approach/contact targets near object start |
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

## Current Skill (Q=0.324) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
- id: contact_1
  type: contact
  generator: impedance_motion
  control: admittance_control
  termination: force_exceeded
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance

```

## Design Metrics

- **Composite score**: 0.324
- **task_score** (E): 0.425
- **fitness_score**: 0.467  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1341 |
| descend_1 | 0.67 | 1.00 | 0.1204 |
| push_1 | 1.00 | 1.00 | 0.1599 |
| retract_1 | 0.00 | 1.00 | 0.1640 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.493, 0.012, 0.175) | (0.496, 0.001, 0.025)→(0.496, 0.001, 0.025) | 0.152→0.152 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_1 | descend | 0.67 / force_exceeded | (0.493, 0.012, 0.175)→(0.492, 0.013, 0.056) | (0.496, 0.001, 0.025)→(0.496, 0.001, 0.025) | 0.152→0.152 | 1.00 / 4.667 | 50595.773 | 0.245 |
| push_1 | push | 1.00 / step_budget | (0.492, 0.013, 0.056)→(0.495, -0.145, 0.046) | (0.496, 0.001, 0.025)→(0.497, -0.060, 0.025) | 0.152→0.092 | 1.00 / 4.000 | 0.245 | 82.404 |
| retract_1 | retract | 0.00 / step_budget | (0.495, -0.145, 0.046)→(0.495, -0.062, 0.187) | (0.497, -0.060, 0.025)→(0.497, -0.060, 0.025) | 0.092→0.092 | 1.00 / 4.000 | 0.245 | 0.245 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.524
- lateral_force_integral: None
- approach_alignment: 0.727
- goal_progress: 0.516
- terminal_score: 0.516
- phase_score: 0.523
- phase_breakdown.reach_object_score: 0.238
- phase_breakdown.reach_goal_score: 0.646

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.521
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.516
- **Median Q (composite search score)**: 0.444
- **K-run variance**: 0.0331
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.385


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `1efc9b29f7d131941a1bd842274a029ca5b2a2ff6a8656033ab118e32e2fae7d`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `6150c547b3cd2920ed4582689733d59ef61d18dc295ccd2a0d2317d1cf4e7764`; realized-scene SHA-256: `79fe20ee7316d80bc617c84166fccacf882b4f96b2faf4b155be83e4f318b183`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51644,-0.02763,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.01644,-0.12237,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.51644,-0.02763,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.09479,"average_solve_count":211.0,"average_success_count":211.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.1642,"approach_1.arc_height":0.11141,"descend_1.contact_force":10.64679,"push_1.push_distance":0.02029,"push_1.push_speed":0.02513},"optimized_scores":{"best_composite_score":0.44417,"best_fitness_score":0.50417,"best_task_score":0.50055},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":623.0,"contact_point_centroid":[0.51796,-0.05372,0.04951],"force_p95":80.35431,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":81.58654,"mean_force":54.81126,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50903,-0.05835,0.0527]},{"body_a":"world","body_b":"push_box","contact_count":2629.0,"contact_point_centroid":[0.51355,-0.06917,-0.00015],"force_p95":45.33474,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":49.31208,"mean_force":13.3424,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50331,-0.0944,0.0495]},{"body_a":"world","body_b":"push_box","contact_count":1696.0,"contact_point_centroid":[0.51644,-0.02763,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50595,0.00606,0.24101]},{"body_a":"world","body_b":"push_box","contact_count":2692.0,"contact_point_centroid":[0.51644,-0.02763,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51178,-0.01812,0.12012]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.51029,-0.0892,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49243,-0.1155,0.11207]}],"total_contact_groups":5},"final_pose_error":0.13832,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51029,-0.0892,0.02499],"final_tcp_position":[0.49439,-0.0715,0.18173],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51644,-0.02763,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":424.0,"n_steps_budget":750.0,"object_pos_end":[0.51644,-0.02763,0.02499],"object_pos_start":[0.51644,-0.02763,0.025],"object_to_goal_dist_end":0.12347,"object_to_goal_dist_start":0.12347,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1696.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.51267,-0.01845,0.18971],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.16502,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":673.0,"n_steps_budget":870.0,"object_pos_end":[0.51644,-0.02763,0.02499],"object_pos_start":[0.51644,-0.02763,0.02499],"object_to_goal_dist_end":0.12347,"object_to_goal_dist_start":0.12347,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2692.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.51337,-0.01774,0.05467],"tcp_start":[0.51267,-0.01845,0.18971],"tcp_to_object_dist_end":0.03143,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51029,-0.0892,0.02499],"object_pos_start":[0.51644,-0.02763,0.02499],"object_to_goal_dist_end":0.06167,"object_to_goal_dist_start":0.12347,"object_z_max":0.0353,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3252.0,"raw_peak_contact_force":81.58654,"subtask_id":"reach_goal","tcp_end":[0.49404,-0.16163,0.04499],"tcp_start":[0.51337,-0.01774,0.05467],"tcp_to_object_dist_end":0.07688,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51029,-0.0892,0.02499],"object_pos_start":[0.51029,-0.0892,0.02499],"object_to_goal_dist_end":0.06167,"object_to_goal_dist_start":0.06167,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49439,-0.0715,0.18173],"tcp_start":[0.49404,-0.16163,0.04499],"tcp_to_object_dist_end":0.15854,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `88c86884172a74f1f27b08fda534b767baf4d8d60d3fd4d782dec9555f4aae87`; realized-scene SHA-256: `258b33ff0697721ed1ba4810cf28d81707440dffd73b12c632f307c6591915c0`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50142,0.05406,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.00142,-0.20406,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.50142,0.05406,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90909,"average_solve_count":143.0,"average_success_count":143.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.23071,"approach_1.arc_height":0.18204,"descend_1.contact_force":14.58813,"push_1.push_distance":0.0218,"push_1.push_speed":0.09758},"optimized_scores":{"best_composite_score":0.06666,"best_fitness_score":0.37666,"best_task_score":0.25748},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":314.0,"contact_point_centroid":[0.50326,0.02415,0.05169],"force_p95":65.19806,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":68.80903,"mean_force":37.39961,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49609,0.01687,0.05478]},{"body_a":"world","body_b":"push_box","contact_count":3133.0,"contact_point_centroid":[0.50173,0.01187,-6e-05],"force_p95":29.55804,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.97831,"mean_force":4.04518,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4952,-0.04864,0.05047]},{"body_a":"world","body_b":"push_box","contact_count":940.0,"contact_point_centroid":[0.50142,0.05406,-0.0],"force_p95":0.24532,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49891,0.0234,0.28277]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49718,0.05432,0.157]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.50151,0.00151,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4935,-0.0894,0.1178]}],"total_contact_groups":5},"final_pose_error":0.12018,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50151,0.00151,0.02499],"final_tcp_position":[0.49526,-0.05205,0.19179],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":68.80903,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":235.0,"n_steps_budget":600.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":940.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.49903,0.04627,0.26114],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.23629,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.49738,0.06238,0.05887],"tcp_start":[0.49903,0.04627,0.26114],"tcp_to_object_dist_end":0.03512,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50151,0.00151,0.02499],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.15152,"object_to_goal_dist_start":0.20406,"object_z_max":0.03528,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3447.0,"raw_peak_contact_force":68.80903,"subtask_id":"reach_goal","tcp_end":[0.49537,-0.12827,0.0465],"tcp_start":[0.49738,0.06238,0.05887],"tcp_to_object_dist_end":0.13169,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50151,0.00151,0.02499],"object_pos_start":[0.50151,0.00151,0.02499],"object_to_goal_dist_end":0.15152,"object_to_goal_dist_start":0.15152,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49526,-0.05205,0.19179],"tcp_start":[0.49537,-0.12827,0.0465],"tcp_to_object_dist_end":0.1753,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a3cdbd735282928b0caf1de02aaaeed7f0a3d0a10908989412c558d20f3517fa`; realized-scene SHA-256: `8c36a5f9300ba3a57ccc09620ec8ba0a5276276ed83fb4303679e150911bfa14`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47139,-0.02418,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02861,-0.12582,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47139,-0.02418,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.58824,"average_solve_count":170.0,"average_success_count":170.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05024,"approach_1.arc_height":0.10664,"descend_1.contact_force":9.35689,"push_1.push_distance":0.02072,"push_1.push_speed":0.04192},"optimized_scores":{"best_composite_score":0.46054,"best_fitness_score":0.52054,"best_task_score":0.51624},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":738.0,"contact_point_centroid":[0.48548,-0.05089,0.04876],"force_p95":93.06404,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":96.81738,"mean_force":64.65049,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47678,-0.0546,0.05312]},{"body_a":"world","body_b":"push_box","contact_count":2545.0,"contact_point_centroid":[0.47765,-0.05974,-0.00021],"force_p95":80.07645,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":94.01102,"mean_force":19.16364,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47986,-0.07215,0.05128]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48369,0.05799,0.18902]},{"body_a":"world","body_b":"push_box","contact_count":680.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46577,0.00061,0.06422]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.47852,-0.09139,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49289,-0.10235,0.1149]}],"total_contact_groups":5},"final_pose_error":0.12901,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47852,-0.09139,0.02499],"final_tcp_position":[0.49478,-0.06151,0.18672],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.46821,0.00739,0.07479],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.05905,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":170.0,"n_steps_budget":600.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":680.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.46497,-0.00561,0.05589],"tcp_start":[0.46821,0.00739,0.07479],"tcp_to_object_dist_end":0.03662,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47852,-0.09139,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.06242,"object_to_goal_dist_start":0.12903,"object_z_max":0.0353,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3283.0,"raw_peak_contact_force":96.81738,"subtask_id":"reach_goal","tcp_end":[0.49465,-0.14511,0.04562],"tcp_start":[0.46497,-0.00561,0.05589],"tcp_to_object_dist_end":0.05977,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47852,-0.09139,0.02499],"object_pos_start":[0.47852,-0.09139,0.02499],"object_to_goal_dist_end":0.06242,"object_to_goal_dist_start":0.06242,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49478,-0.06151,0.18672],"tcp_start":[0.49465,-0.14511,0.04562],"tcp_to_object_dist_end":0.16527,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```