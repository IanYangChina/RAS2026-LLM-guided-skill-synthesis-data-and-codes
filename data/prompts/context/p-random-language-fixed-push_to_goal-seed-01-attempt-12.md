## Search State

- **Seed**: 1
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 5 | 0.1058 | 0.53 | ❌ rejected |
| 11 | approach → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | time_limit | time_limit | 7 | -0.0270 | 0.44 | ❌ rejected |
| 10 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 5 | 0.5536 | 0.58 | ❌ rejected |
| 9 | approach → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.3963 | 0.67 | ✅ accepted |
| 8 | approach → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.3216 | 0.50 | ❌ rejected |

**Proposal policy**: task_score is 0.53 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.106) — your mutation base

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

- **Composite score**: 0.106
- **task_score** (E): 0.531
- **fitness_score**: 0.416  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.1896 |
| contact | 0.00 | 1.00 | 0.1107 |
| push | 1.00 | 1.00 | 0.0816 |
| retract | 1.00 | 1.00 | 0.0410 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.473, 0.074, 0.132) | (0.474, -0.001, 0.025)→(0.474, -0.001, 0.025) | 0.154→0.154 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact | contact | 0.00 / step_budget | (0.473, 0.074, 0.132)→(0.474, 0.041, 0.027) | (0.474, -0.001, 0.025)→(0.474, -0.001, 0.025) | 0.154→0.154 | 1.00 / 4.000 | 0.245 | 0.245 |
| push | push | 1.00 / time_limit | (0.474, 0.041, 0.027)→(0.483, -0.039, 0.022) | (0.474, -0.001, 0.025)→(0.490, -0.076, 0.026) | 0.154→0.077 | 1.00 / 2.667 | 8.533 | 16.302 |
| retract | retract | 1.00 / step_budget | (0.483, -0.039, 0.022)→(0.479, -0.039, 0.062) | (0.490, -0.076, 0.026)→(0.489, -0.077, 0.025) | 0.077→0.076 | 1.00 / 4.000 | 0.245 | 8.642 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.607
- lateral_force_integral: None
- approach_alignment: 0.614
- goal_progress: 0.606
- terminal_score: 0.606
- phase_score: 0.374
- phase_breakdown.approach_score: 0.113
- phase_breakdown.push_score: 0.275
- phase_breakdown.contact_score: 0.713

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.467
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.608
- **Median Q (composite search score)**: 0.156
- **K-run variance**: 0.0051
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.315


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.065,"average_solve_count":200.0,"average_success_count":200.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.02178,"contact.contact_force_threshold":8.50463,"contact.contact_offset_x":0.00712,"push.push_distance":0.14423,"push.push_speed":0.04856},"optimized_scores":{"best_composite_score":0.00449,"best_fitness_score":0.31449,"best_task_score":0.37833},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":888.0,"contact_point_centroid":[0.50525,0.04041,0.03396],"force_p95":9.78297,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.04356,"mean_force":3.28845,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49873,0.0522,0.02117]},{"body_a":"world","body_b":"push_box","contact_count":1708.0,"contact_point_centroid":[0.50527,-0.02315,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.40982,"mean_force":0.25813,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49434,0.01397,0.0417]},{"body_a":"world","body_b":"push_box","contact_count":1896.0,"contact_point_centroid":[0.50312,0.0105,-4e-05],"force_p95":4.98712,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.37965,"mean_force":1.87601,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49909,0.05832,0.02149]},{"body_a":"push_box","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.5301,-0.00246,0.05014],"force_p95":8.4891,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.72191,"mean_force":6.39381,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49803,0.01416,0.02091]},{"body_a":"push_box","body_b":"link7","contact_count":64.0,"contact_point_centroid":[0.53004,0.01033,0.05024],"force_p95":5.54939,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.54015,"mean_force":1.84121,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49815,0.0233,0.02093]},{"body_a":"attachment","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.51262,0.0024,0.05012],"force_p95":2.71986,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.0533,"mean_force":1.23195,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49793,0.0141,0.0209]},{"body_a":"world","body_b":"push_box","contact_count":3284.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.4981,0.06254,0.2136]},{"body_a":"world","body_b":"push_box","contact_count":2392.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.49953,0.11015,0.07529]}],"total_contact_groups":8},"final_pose_error":0.00995,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50547,-0.02326,0.02499],"final_tcp_position":[0.49411,0.01399,0.06178],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":13.04356,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":821.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3284.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.49809,0.12597,0.12949],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.1269,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":598.0,"n_steps_budget":690.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2392.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.50361,0.09517,0.02619],"tcp_start":[0.49809,0.12597,0.12949],"tcp_to_object_dist_end":0.04119,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50569,-0.02262,0.02511],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.12751,"object_to_goal_dist_start":0.20406,"object_z_max":0.0253,"peak_contact_force":9.37965,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2848.0,"raw_peak_contact_force":13.04356,"subtask_id":"push","tcp_end":[0.49803,0.01419,0.02092],"tcp_start":[0.50361,0.09517,0.02619],"tcp_to_object_dist_end":0.03783,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":434.0,"n_steps_budget":600.0,"object_pos_end":[0.50547,-0.02326,0.02499],"object_pos_start":[0.50569,-0.02262,0.02511],"object_to_goal_dist_end":0.12686,"object_to_goal_dist_start":0.12751,"object_z_max":0.02511,"peak_contact_force":0.24525,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1714.0,"raw_peak_contact_force":11.40982,"tcp_end":[0.49411,0.01399,0.06178],"tcp_start":[0.49803,0.01419,0.02092],"tcp_to_object_dist_end":0.05358,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.07447,"average_solve_count":188.0,"average_success_count":188.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.03526,"contact.contact_force_threshold":6.39229,"contact.contact_offset_x":0.00472,"push.push_distance":0.16371,"push.push_speed":0.04987},"optimized_scores":{"best_composite_score":0.15694,"best_fitness_score":0.46694,"best_task_score":0.60608},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1930.0,"contact_point_centroid":[0.48005,-0.06571,-3e-05],"force_p95":9.11377,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.16047,"mean_force":2.3212,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.47451,-0.01921,0.02244]},{"body_a":"attachment","body_b":"push_box","contact_count":897.0,"contact_point_centroid":[0.48284,-0.03711,0.03571],"force_p95":9.485,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.23568,"mean_force":3.64012,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.47534,-0.02513,0.0221]},{"body_a":"world","body_b":"push_box","contact_count":1570.0,"contact_point_centroid":[0.486,-0.10179,-3e-05],"force_p95":0.25,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.87783,"mean_force":0.26959,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.47887,-0.06269,0.0432]},{"body_a":"push_box","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.51377,-0.08743,0.05077],"force_p95":9.55798,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.73434,"mean_force":3.53684,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.48243,-0.06307,0.02181]},{"body_a":"push_box","body_b":"link7","contact_count":165.0,"contact_point_centroid":[0.51224,-0.0725,0.05034],"force_p95":7.28885,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.13731,"mean_force":4.56552,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.4804,-0.05279,0.02177]},{"body_a":"attachment","body_b":"push_box","contact_count":10.0,"contact_point_centroid":[0.49865,-0.07512,0.05148],"force_p95":3.04047,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.45742,"mean_force":1.48352,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.48201,-0.06308,0.02216]},{"body_a":"world","body_b":"push_box","contact_count":2432.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.48465,0.02498,0.21727]},{"body_a":"world","body_b":"push_box","contact_count":2544.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.46965,0.03424,0.07816]}],"total_contact_groups":8},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48609,-0.10111,0.02499],"final_tcp_position":[0.4787,-0.06265,0.06262],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":19.16047,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":608.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2432.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.47039,0.05127,0.13376],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13238,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":636.0,"n_steps_budget":720.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2544.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.4716,0.01763,0.02684],"tcp_start":[0.47039,0.05127,0.13376],"tcp_to_object_dist_end":0.04186,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48852,-0.09982,0.02688],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.05151,"object_to_goal_dist_start":0.12903,"object_z_max":0.02685,"peak_contact_force":14.66415,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2992.0,"raw_peak_contact_force":19.16047,"subtask_id":"push","tcp_end":[0.48255,-0.06298,0.02183],"tcp_start":[0.4716,0.01763,0.02684],"tcp_to_object_dist_end":0.03766,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":412.0,"n_steps_budget":600.0,"object_pos_end":[0.48609,-0.10111,0.02499],"object_pos_start":[0.48852,-0.09982,0.02688],"object_to_goal_dist_end":0.05083,"object_to_goal_dist_start":0.05151,"object_z_max":0.02688,"peak_contact_force":0.24525,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1586.0,"raw_peak_contact_force":11.87783,"tcp_end":[0.4787,-0.06265,0.06262],"tcp_start":[0.48255,-0.06298,0.02183],"tcp_to_object_dist_end":0.05431,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.06965,"average_solve_count":201.0,"average_success_count":201.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.03016,"contact.contact_force_threshold":4.51867,"contact.contact_offset_x":0.00019,"push.push_distance":0.14321,"push.push_speed":0.04999},"optimized_scores":{"best_composite_score":0.15604,"best_fitness_score":0.46604,"best_task_score":0.60764},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":888.0,"contact_point_centroid":[0.46445,-0.04388,0.03509],"force_p95":8.74562,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.7021,"mean_force":3.1693,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.45702,-0.03186,0.02261]},{"body_a":"world","body_b":"push_box","contact_count":1912.0,"contact_point_centroid":[0.46076,-0.07379,-3e-05],"force_p95":5.12431,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.17251,"mean_force":1.81645,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.45513,-0.02557,0.023]},{"body_a":"push_box","body_b":"link7","contact_count":56.0,"contact_point_centroid":[0.49515,-0.06738,0.05017],"force_p95":5.84139,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.05581,"mean_force":2.06879,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.46351,-0.05077,0.02222]},{"body_a":"world","body_b":"push_box","contact_count":1561.0,"contact_point_centroid":[0.47525,-0.10606,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.6372,"mean_force":0.24895,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.46591,-0.06799,0.04239]},{"body_a":"attachment","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.48099,-0.08055,0.04293],"force_p95":1.59658,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.81194,"mean_force":0.68204,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.46937,-0.06837,0.02178]},{"body_a":"world","body_b":"push_box","contact_count":2428.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.47515,0.02167,0.21737]},{"body_a":"world","body_b":"push_box","contact_count":2500.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.44734,0.02724,0.07867]}],"total_contact_groups":7},"final_pose_error":0.00992,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47529,-0.10608,0.02499],"final_tcp_position":[0.46563,-0.06792,0.06265],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":16.7021,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":607.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2428.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.45089,0.0445,0.13395],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.1329,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":625.0,"n_steps_budget":720.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2500.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.44645,0.01033,0.02728],"tcp_start":[0.45089,0.0445,0.13395],"tcp_to_object_dist_end":0.04215,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47541,-0.10529,0.02506],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.05103,"object_to_goal_dist_start":0.12843,"object_z_max":0.02524,"peak_contact_force":1.55381,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2856.0,"raw_peak_contact_force":16.7021,"subtask_id":"push","tcp_end":[0.46941,-0.06829,0.02181],"tcp_start":[0.44645,0.01033,0.02728],"tcp_to_object_dist_end":0.03762,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":394.0,"n_steps_budget":600.0,"object_pos_end":[0.47529,-0.10608,0.02499],"object_pos_start":[0.47541,-0.10529,0.02506],"object_to_goal_dist_end":0.05039,"object_to_goal_dist_start":0.05103,"object_z_max":0.02506,"peak_contact_force":0.24525,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1565.0,"raw_peak_contact_force":2.6372,"tcp_end":[0.46563,-0.06792,0.06265],"tcp_start":[0.46941,-0.06829,0.02181],"tcp_to_object_dist_end":0.05448,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```