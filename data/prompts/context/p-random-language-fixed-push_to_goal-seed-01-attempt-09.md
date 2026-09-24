## Search State

- **Seed**: 1
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.3963 | 0.67 | ✅ accepted |
| 8 | approach → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.3216 | 0.50 | ❌ rejected |
| 7 | approach → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.2823 | 0.60 | ❌ rejected |
| 6 | approach → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.3668 | 0.63 | ✅ accepted |
| 5 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1999 | 0.52 | ❌ rejected |

**Proposal policy**: task_score is 0.67 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.396) — your mutation base

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

- **Composite score**: 0.396
- **task_score** (E): 0.674
- **fitness_score**: 0.656  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.260

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.2745 |
| contact | 1.00 | 1.00 | 0.0393 |
| push | 1.00 | 1.00 | 0.1343 |
| retract | 1.00 | 1.00 | 0.0410 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.472, 0.072, 0.040) | (0.474, -0.001, 0.025)→(0.474, -0.001, 0.025) | 0.154→0.154 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact | align | 1.00 / step_budget | (0.472, 0.072, 0.040)→(0.473, 0.037, 0.024) | (0.474, -0.001, 0.025)→(0.474, -0.001, 0.025) | 0.154→0.154 | 1.00 / 4.000 | 0.245 | 0.245 |
| push | push | 1.00 / step_budget | (0.473, 0.037, 0.024)→(0.489, -0.095, 0.020) | (0.474, -0.001, 0.025)→(0.472, -0.125, 0.025) | 0.154→0.048 | 1.00 / 2.000 | 0.543 | 24.102 |
| retract | retract | 1.00 / step_budget | (0.489, -0.095, 0.020)→(0.485, -0.095, 0.061) | (0.472, -0.125, 0.025)→(0.471, -0.126, 0.025) | 0.048→0.049 | 1.00 / 4.000 | 0.245 | 3.341 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.948
- lateral_force_integral: None
- approach_alignment: 0.706
- goal_progress: 0.709
- terminal_score: 0.709
- phase_score: 0.770
- phase_breakdown.approach_score: 0.820
- phase_breakdown.push_score: 0.749
- phase_breakdown.contact_score: 0.771

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.745
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.735
- **Median Q (composite search score)**: 0.388
- **K-run variance**: 0.0048
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.339


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.75465,"average_solve_count":269.0,"average_success_count":269.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.04002,"contact.contact_offset_x":0.00463,"push.push_distance":0.12484,"push.push_speed":0.01648},"optimized_scores":{"best_composite_score":0.31546,"best_fitness_score":0.57546,"best_task_score":0.73495},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":850.0,"contact_point_centroid":[0.50642,0.00275,0.04056],"force_p95":17.18358,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.61266,"mean_force":5.3885,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49634,0.01447,0.02146]},{"body_a":"world","body_b":"push_box","contact_count":1339.0,"contact_point_centroid":[0.50351,-0.03868,-5e-05],"force_p95":12.13071,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.99113,"mean_force":4.3612,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49643,0.01589,0.02158]},{"body_a":"push_box","body_b":"link7","contact_count":190.0,"contact_point_centroid":[0.52708,-0.01391,0.05096],"force_p95":12.30902,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.225,"mean_force":4.42845,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49625,0.00266,0.02118]},{"body_a":"world","body_b":"push_box","contact_count":1704.0,"contact_point_centroid":[0.50107,-0.0961,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.67613,"mean_force":0.2522,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49263,-0.05805,0.0412]},{"body_a":"attachment","body_b":"push_box","contact_count":8.0,"contact_point_centroid":[0.51102,-0.07026,0.05016],"force_p95":1.72463,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.80776,"mean_force":0.66182,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.4961,-0.05849,0.02029]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49773,0.05863,0.17463]},{"body_a":"world","body_b":"push_box","contact_count":612.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact","phase_type":"align","tcp_position_centroid":[0.49757,0.10521,0.03865]}],"total_contact_groups":7},"final_pose_error":0.00996,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50112,-0.09593,0.02499],"final_tcp_position":[0.49243,-0.05798,0.06116],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":22.61266,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.49736,0.11762,0.05195],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.06917,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":153.0,"n_steps_budget":600.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":612.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.49988,0.09161,0.02675],"tcp_start":[0.49736,0.11762,0.05195],"tcp_to_object_dist_end":0.03763,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50176,-0.09503,0.02511],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.05499,"object_to_goal_dist_start":0.20406,"object_z_max":0.0264,"peak_contact_force":1.62937,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2379.0,"raw_peak_contact_force":22.61266,"subtask_id":"push","tcp_end":[0.49636,-0.05826,0.02031],"tcp_start":[0.49988,0.09161,0.02675],"tcp_to_object_dist_end":0.03748,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":436.0,"n_steps_budget":600.0,"object_pos_end":[0.50112,-0.09593,0.02499],"object_pos_start":[0.50176,-0.09503,0.02511],"object_to_goal_dist_end":0.05409,"object_to_goal_dist_start":0.05499,"object_z_max":0.02513,"peak_contact_force":0.24525,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1712.0,"raw_peak_contact_force":2.67613,"tcp_end":[0.49243,-0.05798,0.06116],"tcp_start":[0.49636,-0.05826,0.02031],"tcp_to_object_dist_end":0.05314,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.76866,"average_solve_count":268.0,"average_success_count":268.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.02507,"contact.contact_offset_x":0.00639,"push.push_distance":0.10472,"push.push_speed":0.02644},"optimized_scores":{"best_composite_score":0.48541,"best_fitness_score":0.74541,"best_task_score":0.70908},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":807.0,"contact_point_centroid":[0.47793,-0.06244,0.02085],"force_p95":14.92096,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.85991,"mean_force":3.89691,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.47866,-0.05068,0.01909]},{"body_a":"world","body_b":"push_box","contact_count":1941.0,"contact_point_centroid":[0.47079,-0.09496,-4e-05],"force_p95":5.8641,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.78782,"mean_force":1.89046,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.47951,-0.05568,0.01921]},{"body_a":"attachment","body_b":"push_box","contact_count":109.0,"contact_point_centroid":[0.48104,-0.12724,0.03498],"force_p95":0.92854,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.11323,"mean_force":0.63292,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.48554,-0.11633,0.03285]},{"body_a":"world","body_b":"push_box","contact_count":1531.0,"contact_point_centroid":[0.46144,-0.14877,-2e-05],"force_p95":0.43793,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.7972,"mean_force":0.26148,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.48545,-0.11631,0.04182]},{"body_a":"push_box","body_b":"link7","contact_count":14.0,"contact_point_centroid":[0.49727,-0.02924,0.05031],"force_p95":1.75513,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.79206,"mean_force":0.72288,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.47172,-0.0064,0.01849]},{"body_a":"world","body_b":"push_box","contact_count":3736.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.48364,0.02604,0.16666]},{"body_a":"world","body_b":"push_box","contact_count":900.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact","phase_type":"align","tcp_position_centroid":[0.46927,0.03293,0.02665]}],"total_contact_groups":7},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.46266,-0.14617,0.02499],"final_tcp_position":[0.48523,-0.11624,0.06076],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":24.85991,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":934.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3736.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.46887,0.05264,0.03404],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07739,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":225.0,"n_steps_budget":600.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":900.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.47216,0.01346,0.02206],"tcp_start":[0.46887,0.05264,0.03404],"tcp_to_object_dist_end":0.03776,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4641,-0.14538,0.02507],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.03619,"object_to_goal_dist_start":0.12903,"object_z_max":0.02535,"peak_contact_force":0.0,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2762.0,"raw_peak_contact_force":24.85991,"subtask_id":"push","tcp_end":[0.48911,-0.11692,0.01993],"tcp_start":[0.47216,0.01346,0.02206],"tcp_to_object_dist_end":0.03823,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":437.0,"n_steps_budget":600.0,"object_pos_end":[0.46266,-0.14617,0.02499],"object_pos_start":[0.4641,-0.14538,0.02507],"object_to_goal_dist_end":0.03754,"object_to_goal_dist_start":0.03619,"object_z_max":0.0251,"peak_contact_force":0.24525,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1640.0,"raw_peak_contact_force":2.11323,"tcp_end":[0.48523,-0.11624,0.06076],"tcp_start":[0.48911,-0.11692,0.01993],"tcp_to_object_dist_end":0.05182,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.848,"average_solve_count":250.0,"average_success_count":250.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.03146,"contact.contact_offset_x":0.00229,"push.push_distance":0.09236,"push.push_speed":0.02913},"optimized_scores":{"best_composite_score":0.38806,"best_fitness_score":0.64806,"best_task_score":0.57939},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":711.0,"contact_point_centroid":[0.46091,-0.06273,0.02134],"force_p95":13.43344,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.83394,"mean_force":3.7624,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.46213,-0.0511,0.01966]},{"body_a":"world","body_b":"push_box","contact_count":1952.0,"contact_point_centroid":[0.45128,-0.09385,-4e-05],"force_p95":5.43048,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.35732,"mean_force":1.63097,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.46382,-0.05643,0.01977]},{"body_a":"push_box","body_b":"link7","contact_count":19.0,"contact_point_centroid":[0.47586,-0.01653,0.05009],"force_p95":8.6722,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.11776,"mean_force":4.0073,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.44855,-0.00466,0.01982]},{"body_a":"attachment","body_b":"push_box","contact_count":119.0,"contact_point_centroid":[0.47082,-0.11988,0.04],"force_p95":0.84118,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.23455,"mean_force":0.62449,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.47642,-0.10964,0.03725]},{"body_a":"world","body_b":"push_box","contact_count":1502.0,"contact_point_centroid":[0.44697,-0.13682,-2e-05],"force_p95":0.45599,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.36255,"mean_force":0.25964,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.47663,-0.1097,0.04133]},{"body_a":"world","body_b":"push_box","contact_count":3712.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.47374,0.02259,0.16679]},{"body_a":"world","body_b":"push_box","contact_count":832.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact","phase_type":"align","tcp_position_centroid":[0.44722,0.02633,0.02734]}],"total_contact_groups":7},"final_pose_error":0.00996,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.44817,-0.13477,0.02499],"final_tcp_position":[0.47637,-0.10963,0.061],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":24.83394,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":928.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3712.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.4489,0.04564,0.03445],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07781,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":208.0,"n_steps_budget":600.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":832.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.44793,0.00683,0.02265],"tcp_start":[0.4489,0.04564,0.03445],"tcp_to_object_dist_end":0.03856,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":938.0,"n_steps_budget":1000.0,"object_pos_end":[0.44937,-0.1335,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.05325,"object_to_goal_dist_start":0.12843,"object_z_max":0.02529,"peak_contact_force":0.0002,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2682.0,"raw_peak_contact_force":24.83394,"subtask_id":"push","tcp_end":[0.4802,-0.11027,0.02017],"tcp_start":[0.44793,0.00683,0.02265],"tcp_to_object_dist_end":0.0389,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":420.0,"n_steps_budget":600.0,"object_pos_end":[0.44817,-0.13477,0.02499],"object_pos_start":[0.44937,-0.1335,0.02499],"object_to_goal_dist_end":0.05402,"object_to_goal_dist_start":0.05325,"object_z_max":0.02509,"peak_contact_force":0.24525,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1621.0,"raw_peak_contact_force":5.23455,"tcp_end":[0.47637,-0.10963,0.061],"tcp_start":[0.4802,-0.11027,0.02017],"tcp_to_object_dist_end":0.05219,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```