## Search State

- **Seed**: 1
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 5 | 0.5536 | 0.58 | ❌ rejected |
| 9 | approach → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.3963 | 0.67 | ✅ accepted |
| 8 | approach → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.3216 | 0.50 | ❌ rejected |
| 7 | approach → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.2823 | 0.60 | ❌ rejected |
| 6 | approach → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.3668 | 0.63 | ✅ accepted |

**Proposal policy**: task_score is 0.58 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| approach | object | (0.00, 0.08, 0.00) | distance | — |
| contact | object | (0.00, 0.03, 0.00) | distance | — |
| push | goal | (0.00, 0.03, 0.00) | distance | push_depth |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=0.554) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
phases:
- id: approach
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.08
    - 0.0
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach
- id: contact
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.03
    - 0.0
  parameters:
    contact_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
  subtask_id: contact
- id: push
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.15
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: positive
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_limit
    when: during_phase
    predicate: force_below
    threshold: 25.0
    on_failure: abort
  subtask_id: push
- id: retract
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
    - 0.05

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.08, 0.0]
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **contact** (`align`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.03, 0.0]
  - parameter_bindings:
    - contact_offset_x: status=consumed; consumers=target.offset.x (add)
- **push** (`push`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.15, mode=replace_offset_projection, sign=positive}
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_limit, when=during_phase, predicate=force_below, on_failure=abort, threshold=25.0
- **retract** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.05]
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.554
- **task_score** (E): 0.583
- **fitness_score**: 0.530  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.2745 |
| contact | 1.00 | 1.00 | 0.0373 |
| push | 0.67 | 1.00 | 0.0879 |
| retract | 1.00 | 1.00 | 0.0410 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.472, 0.072, 0.040) | (0.474, -0.001, 0.025)→(0.474, -0.001, 0.025) | 0.154→0.154 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact | contact | 1.00 / force_exceeded | (0.472, 0.072, 0.040)→(0.469, 0.036, 0.030) | (0.474, -0.001, 0.025)→(0.474, -0.001, 0.025) | 0.154→0.154 | 1.00 / 5.000 | 21.663 | 0.245 |
| push | push | 0.67 / time_limit | (0.469, 0.036, 0.030)→(0.482, -0.049, 0.024) | (0.474, -0.001, 0.025)→(0.492, -0.085, 0.026) | 0.154→0.068 | 1.00 / 3.333 | 10.516 | 24.668 |
| retract | retract | 1.00 / step_budget | (0.477, -0.073, 0.021)→(0.473, -0.073, 0.062) | (0.482, -0.110, 0.025)→(0.482, -0.111, 0.025) | 0.045→0.044 | 1.00 / 4.000 | 0.245 | 4.163 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.835
- lateral_force_integral: None
- approach_alignment: 0.651
- goal_progress: 0.820
- terminal_score: 0.820
- phase_score: 0.636
- phase_breakdown.approach_score: 0.820
- phase_breakdown.push_score: 0.481
- phase_breakdown.contact_score: 0.772

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.710
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.820
- **Median Q (composite search score)**: 0.521
- **K-run variance**: 0.0183
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.244


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.11184,"average_solve_count":152.0,"average_success_count":152.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.04686,"contact.contact_force_threshold":4.20664,"push.push_distance":0.2007,"push.push_speed":0.06879,"push.push_time":5.19582},"optimized_scores":{"best_composite_score":0.40705,"best_fitness_score":0.38371,"best_task_score":0.4319},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1213.0,"contact_point_centroid":[0.51068,-0.0068,-7e-05],"force_p95":12.28695,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.85087,"mean_force":4.67228,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49198,0.04678,0.03197]},{"body_a":"attachment","body_b":"push_box","contact_count":707.0,"contact_point_centroid":[0.50201,0.03164,0.04657],"force_p95":16.5701,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.13094,"mean_force":6.06661,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49191,0.04305,0.03158]},{"body_a":"push_box","body_b":"link7","contact_count":99.0,"contact_point_centroid":[0.53016,-0.00964,0.0558],"force_p95":18.74977,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.17212,"mean_force":10.27663,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49282,0.00413,0.02931]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49773,0.05863,0.17463]},{"body_a":"world","body_b":"push_box","contact_count":752.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.49482,0.10466,0.04407]}],"total_contact_groups":5},"final_pose_error":0.14525,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51117,-0.0347,0.02939],"final_tcp_position":[0.49331,-0.00161,0.02934],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":25.85087,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.49736,0.11762,0.05195],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.06917,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":188.0,"n_steps_budget":600.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.02499,"peak_contact_force":24.04128,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":752.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49459,0.09097,0.03868],"tcp_start":[0.49736,0.11762,0.05195],"tcp_to_object_dist_end":0.03996,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":832.0,"n_steps_budget":1000.0,"object_pos_end":[0.51117,-0.0347,0.02939],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.11593,"object_to_goal_dist_start":0.20406,"object_z_max":0.02941,"peak_contact_force":25.85087,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2019.0,"raw_peak_contact_force":25.85087,"subtask_id":"push","tcp_end":[0.49331,-0.00161,0.02934],"tcp_start":[0.49459,0.09097,0.03868],"tcp_to_object_dist_end":0.0376,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.28205,"average_solve_count":156.0,"average_success_count":156.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.06557,"contact.contact_force_threshold":6.53477,"push.push_distance":0.15426,"push.push_speed":0.03827,"push.push_time":6.97346},"optimized_scores":{"best_composite_score":0.52066,"best_fitness_score":0.49732,"best_task_score":0.49627},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1381.0,"contact_point_centroid":[0.48603,-0.06983,-0.00011],"force_p95":18.46539,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.46095,"mean_force":8.33903,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.46933,-0.01904,0.02213]},{"body_a":"attachment","body_b":"push_box","contact_count":942.0,"contact_point_centroid":[0.48518,-0.03064,0.04741],"force_p95":13.95679,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.08797,"mean_force":7.99988,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.46929,-0.0189,0.02208]},{"body_a":"push_box","body_b":"link7","contact_count":694.0,"contact_point_centroid":[0.49805,-0.03847,0.0517],"force_p95":12.1608,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.01217,"mean_force":8.49494,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.46867,-0.01597,0.02206]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.4864,-0.0626,0.04146],"force_p95":7.0206,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.55042,"mean_force":3.81061,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.4753,-0.05051,0.02119]},{"body_a":"world","body_b":"push_box","contact_count":1581.0,"contact_point_centroid":[0.48002,-0.0882,-1e-05],"force_p95":0.24638,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.9613,"mean_force":0.25574,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.47177,-0.05027,0.04184]},{"body_a":"push_box","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.5058,-0.0665,0.05007],"force_p95":2.36057,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.45835,"mean_force":1.48062,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.47514,-0.05056,0.02115]},{"body_a":"world","body_b":"push_box","contact_count":3616.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.48364,0.02608,0.16652]},{"body_a":"world","body_b":"push_box","contact_count":1024.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.46596,0.03332,0.02861]}],"total_contact_groups":8},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48,-0.08816,0.02499],"final_tcp_position":[0.4715,-0.05024,0.06198],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":23.46095,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":904.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3616.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.46887,0.05263,0.03407],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07739,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":256.0,"n_steps_budget":630.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":21.88174,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.46583,0.01279,0.02598],"tcp_start":[0.46887,0.05263,0.03407],"tcp_to_object_dist_end":0.0374,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48083,-0.08748,0.02495],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.0654,"object_to_goal_dist_start":0.12903,"object_z_max":0.0301,"peak_contact_force":4.10325,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3017.0,"raw_peak_contact_force":23.46095,"subtask_id":"push","tcp_end":[0.47533,-0.05048,0.02121],"tcp_start":[0.46583,0.01279,0.02598],"tcp_to_object_dist_end":0.03759,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":400.0,"n_steps_budget":600.0,"object_pos_end":[0.48,-0.08816,0.02499],"object_pos_start":[0.48083,-0.08748,0.02495],"object_to_goal_dist_end":0.065,"object_to_goal_dist_start":0.0654,"object_z_max":0.02507,"peak_contact_force":0.24525,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1586.0,"raw_peak_contact_force":7.55042,"tcp_end":[0.4715,-0.05024,0.06198],"tcp_start":[0.47533,-0.05048,0.02121],"tcp_to_object_dist_end":0.05366,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.10857,"average_solve_count":175.0,"average_success_count":175.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.05348,"contact.contact_force_threshold":9.01496,"push.push_distance":0.15852,"push.push_speed":0.06702,"push.push_time":6.63577},"optimized_scores":{"best_composite_score":0.73303,"best_fitness_score":0.70969,"best_task_score":0.81996},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":905.0,"contact_point_centroid":[0.46594,-0.05637,0.03239],"force_p95":12.60698,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.69082,"mean_force":3.98461,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.45988,-0.04438,0.02205]},{"body_a":"world","body_b":"push_box","contact_count":1858.0,"contact_point_centroid":[0.46453,-0.0893,-4e-05],"force_p95":6.21869,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.12509,"mean_force":2.23692,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.45964,-0.04361,0.02211]},{"body_a":"push_box","body_b":"link7","contact_count":29.0,"contact_point_centroid":[0.49892,-0.08212,0.05023],"force_p95":3.03753,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.81714,"mean_force":0.96793,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.46821,-0.06791,0.02149]},{"body_a":"world","body_b":"push_box","contact_count":1649.0,"contact_point_centroid":[0.48383,-0.13349,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.7746,"mean_force":0.24672,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.47478,-0.09531,0.04153]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.48824,-0.10796,0.04033],"force_p95":0.39048,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39391,"mean_force":0.34262,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.47832,-0.09585,0.02101]},{"body_a":"world","body_b":"push_box","contact_count":3704.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.47373,0.0226,0.16673]},{"body_a":"world","body_b":"push_box","contact_count":1032.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.44584,0.02612,0.02912]}],"total_contact_groups":7},"final_pose_error":0.00994,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48379,-0.13351,0.02499],"final_tcp_position":[0.47451,-0.09523,0.06188],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":24.69082,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":926.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3704.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.44889,0.04564,0.0344],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07781,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":258.0,"n_steps_budget":630.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":19.06499,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1032.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.4455,0.00535,0.02647],"tcp_start":[0.44889,0.04564,0.0344],"tcp_to_object_dist_end":0.03727,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48368,-0.13276,0.02503],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.02374,"object_to_goal_dist_start":0.12843,"object_z_max":0.02529,"peak_contact_force":1.59276,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2792.0,"raw_peak_contact_force":24.69082,"subtask_id":"push","tcp_end":[0.47834,-0.09577,0.02104],"tcp_start":[0.4455,0.00535,0.02647],"tcp_to_object_dist_end":0.03759,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":414.0,"n_steps_budget":600.0,"object_pos_end":[0.48379,-0.13351,0.02499],"object_pos_start":[0.48368,-0.13276,0.02503],"object_to_goal_dist_end":0.02312,"object_to_goal_dist_start":0.02374,"object_z_max":0.02503,"peak_contact_force":0.24525,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1652.0,"raw_peak_contact_force":0.7746,"tcp_end":[0.47451,-0.09523,0.06188],"tcp_start":[0.47834,-0.09577,0.02104],"tcp_to_object_dist_end":0.05397,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```