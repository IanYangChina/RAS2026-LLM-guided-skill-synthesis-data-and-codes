## Search State

- **Seed**: 1
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.4534 | 0.40 | ❌ rejected |
| 7 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.6020 | 0.88 | ❌ rejected |
| 6 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.6900 | 0.85 | ❌ rejected |
| 5 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | time_limit | 9 | 0.6934 | 0.88 | ✅ accepted |
| 4 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.6057 | 0.89 | ❌ rejected |

**Proposal policy**: task_score is 0.40 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.453) — your mutation base

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

- **Composite score**: 0.453
- **task_score** (E): 0.401
- **fitness_score**: 0.613  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1141 |
| contact_1 | 1.00 | 1.00 | 0.1444 |
| push_1 | 1.00 | 1.00 | 0.1505 |
| retract_1 | 0.33 | 1.00 | 0.1275 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.474, -0.001, 0.197) | (0.474, -0.001, 0.025)→(0.474, -0.001, 0.025) | 0.154→0.154 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / force_exceeded | (0.474, -0.001, 0.197)→(0.471, -0.001, 0.052) | (0.474, -0.001, 0.025)→(0.474, -0.001, 0.025) | 0.154→0.154 | 1.00 / 5.000 | 48.900 | 0.245 |
| push_1 | push | 1.00 / step_budget | (0.471, -0.001, 0.052)→(0.496, -0.144, 0.021) | (0.474, -0.001, 0.025)→(0.495, -0.056, 0.025) | 0.154→0.095 | 1.00 / 4.000 | 0.245 | 141.633 |
| retract_1 | retract | 0.33 / step_budget | (0.496, -0.144, 0.021)→(0.491, -0.081, 0.132) | (0.495, -0.056, 0.025)→(0.495, -0.056, 0.025) | 0.095→0.095 | 1.00 / 4.000 | 0.245 | 0.953 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.606
- lateral_force_integral: None
- approach_alignment: 0.703
- goal_progress: 0.505
- terminal_score: 0.505
- phase_score: 0.821
- phase_breakdown.push_to_goal_score: 0.901
- phase_breakdown.reach_object_score: 0.634

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.695
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.505
- **Median Q (composite search score)**: 0.499
- **K-run variance**: 0.0082
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.338


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.3112,"average_solve_count":241.0,"average_success_count":241.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.19095,"approach_1.speed":0.04305,"contact_1.force_threshold":3.25876,"contact_1.speed":0.03278,"push_1.push_distance":0.19533,"push_1.speed":0.0794,"retract_1.speed":0.08193},"optimized_scores":{"best_composite_score":0.32682,"best_fitness_score":0.48682,"best_task_score":0.27386},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":449.0,"contact_point_centroid":[0.50763,0.02542,0.04795],"force_p95":114.1391,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":119.7306,"mean_force":80.20155,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49942,0.01849,0.04868]},{"body_a":"world","body_b":"push_box","contact_count":2958.0,"contact_point_centroid":[0.5003,0.00728,-0.00013],"force_p95":72.27635,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":88.46482,"mean_force":12.48992,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49657,-0.05029,0.03494]},{"body_a":"world","body_b":"push_box","contact_count":1348.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49859,0.0225,0.26105]},{"body_a":"world","body_b":"push_box","contact_count":3920.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49675,0.04955,0.13475]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.49953,-0.00182,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49338,-0.09398,0.0808]}],"total_contact_groups":5},"final_pose_error":0.06413,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49953,-0.00182,0.02499],"final_tcp_position":[0.49481,-0.05176,0.13503],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":119.7306,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":337.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1348.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.49871,0.04683,0.22202],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.19718,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":980.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.02499,"peak_contact_force":53.77211,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3920.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.49716,0.05244,0.05239],"tcp_start":[0.49871,0.04683,0.22202],"tcp_to_object_dist_end":0.02778,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49953,-0.00182,0.02499],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.14818,"object_to_goal_dist_start":0.20406,"object_z_max":0.03529,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3407.0,"raw_peak_contact_force":119.7306,"subtask_id":"push_to_goal","tcp_end":[0.49585,-0.12733,0.02192],"tcp_start":[0.49716,0.05244,0.05239],"tcp_to_object_dist_end":0.1256,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49953,-0.00182,0.02499],"object_pos_start":[0.49953,-0.00182,0.02499],"object_to_goal_dist_end":0.14818,"object_to_goal_dist_start":0.14818,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49481,-0.05176,0.13503],"tcp_start":[0.49585,-0.12733,0.02192],"tcp_to_object_dist_end":0.12093,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.79402,"average_solve_count":301.0,"average_success_count":301.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.14413,"approach_1.speed":0.06586,"contact_1.force_threshold":3.46683,"contact_1.speed":0.02604,"push_1.push_distance":0.139,"push_1.speed":0.01792,"retract_1.speed":0.08728},"optimized_scores":{"best_composite_score":0.49852,"best_fitness_score":0.65852,"best_task_score":0.42359},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":596.0,"contact_point_centroid":[0.48915,-0.0545,0.0464],"force_p95":143.81833,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":152.40429,"mean_force":102.2003,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47991,-0.05982,0.04702]},{"body_a":"world","body_b":"push_box","contact_count":2537.0,"contact_point_centroid":[0.47838,-0.06216,-0.00028],"force_p95":127.04837,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":149.26237,"mean_force":24.47643,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48487,-0.09177,0.03738]},{"body_a":"world","body_b":"push_box","contact_count":1632.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48557,-0.01038,0.23998]},{"body_a":"world","body_b":"push_box","contact_count":3188.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46847,-0.02252,0.11395]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.47935,-0.07855,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48838,-0.13091,0.08831]}],"total_contact_groups":5},"final_pose_error":0.02931,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47935,-0.07855,0.02499],"final_tcp_position":[0.48052,-0.09629,0.15169],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":152.40429,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":408.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1632.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.47169,-0.02156,0.17858],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.15361,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":797.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":49.89013,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3188.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.46781,-0.02355,0.05247],"tcp_start":[0.47169,-0.02156,0.17858],"tcp_to_object_dist_end":0.02772,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":925.0,"n_steps_budget":1000.0,"object_pos_end":[0.47935,-0.07855,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.07437,"object_to_goal_dist_start":0.12903,"object_z_max":0.03513,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3133.0,"raw_peak_contact_force":152.40429,"subtask_id":"push_to_goal","tcp_end":[0.49657,-0.15242,0.02121],"tcp_start":[0.46781,-0.02355,0.05247],"tcp_to_object_dist_end":0.07595,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47935,-0.07855,0.02499],"object_pos_start":[0.47935,-0.07855,0.02499],"object_to_goal_dist_end":0.07437,"object_to_goal_dist_start":0.07437,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.48052,-0.09629,0.15169],"tcp_start":[0.49657,-0.15242,0.02121],"tcp_to_object_dist_end":0.12794,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.83936,"average_solve_count":249.0,"average_success_count":249.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15588,"approach_1.speed":0.06947,"contact_1.force_threshold":2.54611,"contact_1.speed":0.02257,"push_1.push_distance":0.13647,"push_1.speed":0.04398,"retract_1.speed":0.05786},"optimized_scores":{"best_composite_score":0.53479,"best_fitness_score":0.69479,"best_task_score":0.50517},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":2054.0,"contact_point_centroid":[0.48906,-0.06924,-0.00032],"force_p95":140.99685,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":152.76372,"mean_force":30.9933,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47636,-0.09686,0.03669]},{"body_a":"attachment","body_b":"push_box","contact_count":576.0,"contact_point_centroid":[0.47634,-0.06242,0.04632],"force_p95":142.934,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":151.65725,"mean_force":108.74479,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46744,-0.06824,0.04655]},{"body_a":"world","body_b":"push_box","contact_count":3935.0,"contact_point_centroid":[0.50536,-0.08624,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.36932,"mean_force":0.24986,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49572,-0.11714,0.06295]},{"body_a":"attachment","body_b":"push_box","contact_count":21.0,"contact_point_centroid":[0.49678,-0.11013,0.05044],"force_p95":0.65509,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.76692,"mean_force":0.50671,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49476,-0.1219,0.05078]},{"body_a":"world","body_b":"push_box","contact_count":1584.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47662,-0.01351,0.24536]},{"body_a":"world","body_b":"push_box","contact_count":3540.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44894,-0.02936,0.11952]}],"total_contact_groups":6},"final_pose_error":0.06755,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50522,-0.08666,0.02499],"final_tcp_position":[0.49844,-0.09519,0.10837],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":152.76372,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":396.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1584.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.45306,-0.02806,0.18971],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.16478,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":885.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":43.0384,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3540.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.44731,-0.03077,0.05244],"tcp_start":[0.45306,-0.02806,0.18971],"tcp_to_object_dist_end":0.02762,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":855.0,"n_steps_budget":1000.0,"object_pos_end":[0.50549,-0.08653,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.0637,"object_to_goal_dist_start":0.12843,"object_z_max":0.03521,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2630.0,"raw_peak_contact_force":152.76372,"subtask_id":"push_to_goal","tcp_end":[0.49664,-0.15093,0.02115],"tcp_start":[0.44731,-0.03077,0.05244],"tcp_to_object_dist_end":0.06511,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50522,-0.08666,0.02499],"object_pos_start":[0.50549,-0.08653,0.02499],"object_to_goal_dist_end":0.06355,"object_to_goal_dist_start":0.0637,"object_z_max":0.02555,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3956.0,"raw_peak_contact_force":2.36932,"tcp_end":[0.49844,-0.09519,0.10837],"tcp_start":[0.49664,-0.15093,0.02115],"tcp_to_object_dist_end":0.08409,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```