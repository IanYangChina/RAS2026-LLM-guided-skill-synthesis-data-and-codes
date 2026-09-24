## Search State

- **Seed**: 1
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.6964 | 0.86 | ❌ rejected |
| 9 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.6955 | 0.88 | ❌ rejected |
| 8 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.4534 | 0.40 | ❌ rejected |
| 7 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.6020 | 0.88 | ❌ rejected |
| 6 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.6900 | 0.85 | ❌ rejected |

**Proposal policy**: task_score is 0.86 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.892, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.696) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
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
  control: force_threshold_switch
  termination: force_exceeded
  parameters:
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
- id: push_1
  type: push
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1

```

## Design Metrics

- **Composite score**: 0.696
- **task_score** (E): 0.859
- **fitness_score**: 0.790  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.260

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2822 |
| contact_1 | 0.67 | 1.00 | 0.0385 |
| push_1 | 1.00 | 1.00 | 0.1533 |
| retract_1 | 0.00 | 1.00 | 0.1200 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.472, 0.075, 0.033) | (0.474, -0.001, 0.025)→(0.474, -0.001, 0.025) | 0.154→0.154 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 0.67 / force_exceeded | (0.472, 0.075, 0.033)→(0.469, 0.038, 0.023) | (0.474, -0.001, 0.025)→(0.474, -0.001, 0.025) | 0.154→0.154 | 1.00 / 4.667 | 25302.042 | 0.245 |
| push_1 | push | 1.00 / step_budget | (0.469, 0.038, 0.023)→(0.495, -0.111, 0.020) | (0.474, -0.001, 0.025)→(0.491, -0.148, 0.025) | 0.154→0.022 | 1.00 / 3.333 | 6.610 | 55.068 |
| retract_1 | retract | 0.00 / step_budget | (0.495, -0.111, 0.020)→(0.493, -0.017, 0.094) | (0.491, -0.148, 0.025)→(0.491, -0.149, 0.025) | 0.022→0.022 | 1.00 / 4.000 | 0.245 | 3.433 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.567
- goal_progress: 0.872
- terminal_score: 0.872
- phase_score: 0.826
- phase_breakdown.push_score: 0.861
- phase_breakdown.approach_score: 0.822
- phase_breakdown.contact_score: 0.770

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.844
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.872
- **Median Q (composite search score)**: 0.699
- **K-run variance**: 0.0129
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.453


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.38947,"average_solve_count":190.0,"average_success_count":190.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.0538,"contact_1.speed":0.02387,"push_1.push_distance":0.16779,"retract_1.speed":0.01546},"optimized_scores":{"best_composite_score":0.6994,"best_fitness_score":0.7094,"best_task_score":0.86319},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1516.0,"contact_point_centroid":[0.5023,-0.04061,-0.0001],"force_p95":51.58285,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":69.90783,"mean_force":12.46374,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49458,0.00443,0.01944]},{"body_a":"attachment","body_b":"push_box","contact_count":930.0,"contact_point_centroid":[0.50484,-0.00665,0.03776],"force_p95":43.40543,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":53.45455,"mean_force":14.58059,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49464,0.00475,0.01951]},{"body_a":"push_box","body_b":"link7","contact_count":442.0,"contact_point_centroid":[0.52219,0.02126,0.05166],"force_p95":39.59525,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.54329,"mean_force":20.83136,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49475,0.0421,0.01986]},{"body_a":"world","body_b":"push_box","contact_count":3967.0,"contact_point_centroid":[0.49893,-0.12211,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.43636,"mean_force":0.25063,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49251,-0.04126,0.05737]},{"body_a":"push_box","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.52542,-0.10753,0.0501],"force_p95":6.75691,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.58073,"mean_force":2.4784,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49543,-0.08335,0.01978]},{"body_a":"attachment","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.51093,-0.09517,0.05069],"force_p95":1.39206,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.46098,"mean_force":0.86204,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49546,-0.08332,0.01979]},{"body_a":"world","body_b":"push_box","contact_count":3976.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49774,0.06374,0.16404]},{"body_a":"world","body_b":"push_box","contact_count":3400.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49489,0.10761,0.02404]}],"total_contact_groups":8},"final_pose_error":0.15782,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49883,-0.12211,0.02499],"final_tcp_position":[0.49348,0.00303,0.09287],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":994.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3976.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.49731,0.12754,0.03129],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07387,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":850.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3400.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49604,0.09104,0.02164],"tcp_start":[0.49731,0.12754,0.03129],"tcp_to_object_dist_end":0.03753,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50043,-0.12013,0.02574],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.02988,"object_to_goal_dist_start":0.20406,"object_z_max":0.0299,"peak_contact_force":18.47899,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2888.0,"raw_peak_contact_force":69.90783,"tcp_end":[0.49551,-0.08318,0.01981],"tcp_start":[0.49604,0.09104,0.02164],"tcp_to_object_dist_end":0.03775,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49883,-0.12211,0.02499],"object_pos_start":[0.50043,-0.12013,0.02574],"object_to_goal_dist_end":0.02792,"object_to_goal_dist_start":0.02988,"object_z_max":0.02579,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3976.0,"raw_peak_contact_force":8.43636,"tcp_end":[0.49348,0.00303,0.09287],"tcp_start":[0.49551,-0.08318,0.01981],"tcp_to_object_dist_end":0.14246,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.35673,"average_solve_count":171.0,"average_success_count":171.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.14133,"contact_1.speed":0.02486,"push_1.push_distance":0.10876,"retract_1.speed":0.05611},"optimized_scores":{"best_composite_score":0.83418,"best_fitness_score":0.84418,"best_task_score":0.87169},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1221.0,"contact_point_centroid":[0.48677,-0.10852,-0.00011],"force_p95":49.60316,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":63.00756,"mean_force":14.12654,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48131,-0.06305,0.02025]},{"body_a":"attachment","body_b":"push_box","contact_count":741.0,"contact_point_centroid":[0.48991,-0.06561,0.03672],"force_p95":39.81627,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.37711,"mean_force":17.15383,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47969,-0.05409,0.02044]},{"body_a":"push_box","body_b":"link7","contact_count":371.0,"contact_point_centroid":[0.50116,-0.04471,0.05183],"force_p95":33.60613,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.93786,"mean_force":22.14386,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47346,-0.0216,0.021]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.49298,-0.13712,0.02069],"force_p95":1.39963,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.42801,"mean_force":1.14416,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49447,-0.12528,0.01996]},{"body_a":"world","body_b":"push_box","contact_count":3983.0,"contact_point_centroid":[0.48955,-0.16284,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.96268,"mean_force":0.24679,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49161,-0.07902,0.05646]},{"body_a":"world","body_b":"push_box","contact_count":3424.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48366,0.02611,0.16637]},{"body_a":"world","body_b":"push_box","contact_count":3644.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46594,0.03124,0.02611]}],"total_contact_groups":7},"final_pose_error":0.18985,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48952,-0.16282,0.02499],"final_tcp_position":[0.49268,-0.03052,0.09166],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":63.00756,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":856.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3424.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.46886,0.05266,0.03395],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0774,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":911.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":12.34397,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3644.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.46662,0.01279,0.0227],"tcp_start":[0.46886,0.05266,0.03395],"tcp_to_object_dist_end":0.03735,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":841.0,"n_steps_budget":930.0,"object_pos_end":[0.48992,-0.16184,0.02504],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.01555,"object_to_goal_dist_start":0.12903,"object_z_max":0.03486,"peak_contact_force":0.87014,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2333.0,"raw_peak_contact_force":63.00756,"tcp_end":[0.49448,-0.12523,0.01997],"tcp_start":[0.46662,0.01279,0.0227],"tcp_to_object_dist_end":0.03724,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48952,-0.16282,0.02499],"object_pos_start":[0.48992,-0.16184,0.02504],"object_to_goal_dist_end":0.01656,"object_to_goal_dist_start":0.01555,"object_z_max":0.02505,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3985.0,"raw_peak_contact_force":1.42801,"tcp_end":[0.49268,-0.03052,0.09166],"tcp_start":[0.49448,-0.12523,0.01997],"tcp_to_object_dist_end":0.14819,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.34483,"average_solve_count":174.0,"average_success_count":174.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.26383,"contact_1.speed":0.0191,"push_1.push_distance":0.10125,"retract_1.speed":0.06521},"optimized_scores":{"best_composite_score":0.55548,"best_fitness_score":0.81548,"best_task_score":0.84267},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":709.0,"contact_point_centroid":[0.47069,-0.07098,0.02482],"force_p95":16.81077,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.288,"mean_force":4.60084,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46861,-0.05907,0.02029]},{"body_a":"world","body_b":"push_box","contact_count":1645.0,"contact_point_centroid":[0.46731,-0.09811,-5e-05],"force_p95":7.32179,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.30796,"mean_force":2.279,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46799,-0.05694,0.02048]},{"body_a":"push_box","body_b":"link7","contact_count":15.0,"contact_point_centroid":[0.47875,-0.03274,0.0502],"force_p95":9.08554,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.80237,"mean_force":2.0841,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.45035,-0.01012,0.0206]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.48332,-0.16141,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43551,"mean_force":0.2455,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49095,-0.0757,0.05908]},{"body_a":"world","body_b":"push_box","contact_count":3404.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47375,0.02263,0.1666]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44551,0.02666,0.02706]}],"total_contact_groups":6},"final_pose_error":0.18092,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48332,-0.16141,0.02499],"final_tcp_position":[0.49229,-0.02261,0.09633],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":32.288,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":851.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3404.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.44887,0.04566,0.03429],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07782,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.44574,0.011,0.02409],"tcp_start":[0.44887,0.04566,0.03429],"tcp_to_object_dist_end":0.04284,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":868.0,"n_steps_budget":960.0,"object_pos_end":[0.48336,-0.16125,0.02469],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.02009,"object_to_goal_dist_start":0.12843,"object_z_max":0.02535,"peak_contact_force":0.4803,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2369.0,"raw_peak_contact_force":32.288,"tcp_end":[0.49354,-0.12557,0.01999],"tcp_start":[0.44574,0.011,0.02409],"tcp_to_object_dist_end":0.0374,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48332,-0.16141,0.02499],"object_pos_start":[0.48336,-0.16125,0.02469],"object_to_goal_dist_end":0.02021,"object_to_goal_dist_start":0.02009,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.43551,"tcp_end":[0.49229,-0.02261,0.09633],"tcp_start":[0.49354,-0.12557,0.01999],"tcp_to_object_dist_end":0.15632,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```