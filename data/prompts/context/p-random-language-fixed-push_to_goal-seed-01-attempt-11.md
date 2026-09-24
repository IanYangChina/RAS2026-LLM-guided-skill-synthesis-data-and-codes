## Search State

- **Seed**: 1
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | time_limit | time_limit | 7 | -0.0270 | 0.44 | ❌ rejected |
| 10 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 5 | 0.5536 | 0.58 | ❌ rejected |
| 9 | approach → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.3963 | 0.67 | ✅ accepted |
| 8 | approach → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.3216 | 0.50 | ❌ rejected |
| 7 | approach → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.2823 | 0.60 | ❌ rejected |

**Proposal policy**: task_score is 0.44 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.027) — your mutation base

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

- **Composite score**: -0.027
- **task_score** (E): 0.439
- **fitness_score**: 0.383  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.1832 |
| contact | 1.00 | 1.00 | 0.0934 |
| push | 0.67 | 1.00 | 0.0550 |
| retract | 1.00 | 1.00 | 0.0417 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / time_limit | (0.500, -0.000, 0.301)→(0.479, 0.046, 0.126) | (0.474, -0.001, 0.025)→(0.474, -0.001, 0.025) | 0.154→0.154 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact | align | 1.00 / step_budget | (0.479, 0.046, 0.126)→(0.472, 0.034, 0.038) | (0.474, -0.001, 0.025)→(0.476, -0.001, 0.026) | 0.154→0.154 | 1.00 / 3.667 | 93.914 | 114.840 |
| push | push | 0.67 / time_limit | (0.472, 0.034, 0.038)→(0.484, -0.019, 0.031) | (0.476, -0.001, 0.026)→(0.490, -0.054, 0.026) | 0.154→0.099 | 1.00 / 1.667 | 37.042 | 49.777 |
| retract | retract | 1.00 / time_limit | (0.474, -0.073, 0.024)→(0.470, -0.072, 0.066) | (0.483, -0.110, 0.026)→(0.482, -0.110, 0.025) | 0.044→0.044 | 1.00 / 4.000 | 0.245 | 2.308 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.665
- lateral_force_integral: None
- approach_alignment: 0.630
- goal_progress: 0.663
- terminal_score: 0.663
- phase_score: 0.423
- phase_breakdown.approach_score: 0.156
- phase_breakdown.push_score: 0.319
- phase_breakdown.contact_score: 0.774

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.519
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.663
- **Median Q (composite search score)**: 0.096
- **K-run variance**: 0.0335
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Parameters at upper bound**: push.push_speed
- **Final σ (mean)**: 0.411


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.21277,"average_solve_count":94.0,"average_success_count":94.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.0389,"approach.approach_time":4.9597,"contact.contact_offset_x":-0.00972,"push.push_distance":0.10872,"push.push_speed":0.02367,"push.push_time":7.41798,"retract.retract_time":1.81939},"optimized_scores":{"best_composite_score":-0.28586,"best_fitness_score":0.12414,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":126.0,"contact_point_centroid":[0.50668,0.08146,0.04598],"force_p95":257.6656,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":260.92085,"mean_force":219.19374,"phase_index":1.0,"phase_name":"contact","phase_type":"align","tcp_position_centroid":[0.49614,0.08395,0.04888]},{"body_a":"world","body_b":"push_box","contact_count":1501.0,"contact_point_centroid":[0.50187,0.05771,-0.00016],"force_p95":150.93456,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":208.27679,"mean_force":18.71116,"phase_index":1.0,"phase_name":"contact","phase_type":"align","tcp_position_centroid":[0.49314,0.0759,0.09367]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.51277,0.08334,0.04432],"force_p95":111.12532,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":111.12532,"mean_force":111.12532,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50309,0.08876,0.04604]},{"body_a":"world","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.50453,0.07684,-0.00125],"force_p95":68.75251,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":70.1628,"mean_force":56.05989,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50309,0.08876,0.04604]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49771,0.03507,0.22345]}],"total_contact_groups":5},"final_pose_error":0.14139,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50506,0.05754,0.02717],"final_tcp_position":[0.50315,0.08882,0.04606],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":260.92085,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.49743,0.06953,0.15183],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12784,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":432.0,"n_steps_budget":810.0,"object_pos_end":[0.50508,0.05755,0.02713],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.20762,"object_to_goal_dist_start":0.20406,"object_z_max":0.0271,"peak_contact_force":247.10989,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1627.0,"raw_peak_contact_force":260.92085,"subtask_id":"contact","tcp_end":[0.50309,0.08876,0.04604],"tcp_start":[0.49743,0.06953,0.15183],"tcp_to_object_dist_end":0.03655,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50506,0.05754,0.02717],"object_pos_start":[0.50508,0.05755,0.02713],"object_to_goal_dist_end":0.20762,"object_to_goal_dist_start":0.20762,"object_z_max":0.02713,"peak_contact_force":111.12532,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3.0,"raw_peak_contact_force":111.12532,"subtask_id":"push","tcp_end":[0.50315,0.08882,0.04606],"tcp_start":[0.50309,0.08876,0.04604],"tcp_to_object_dist_end":0.03659,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.07453,"average_solve_count":161.0,"average_success_count":161.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.03292,"approach.approach_time":7.82333,"contact.contact_offset_x":-1e-05,"push.push_distance":0.1073,"push.push_speed":0.04991,"push.push_time":4.5496,"retract.retract_time":2.84048},"optimized_scores":{"best_composite_score":0.10876,"best_fitness_score":0.51876,"best_task_score":0.66275},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":12.0,"contact_point_centroid":[0.46966,-8e-05,0.03995],"force_p95":46.93392,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.19194,"mean_force":23.9712,"phase_index":1.0,"phase_name":"contact","phase_type":"align","tcp_position_centroid":[0.46889,0.01187,0.03878]},{"body_a":"world","body_b":"push_box","contact_count":1106.0,"contact_point_centroid":[0.47148,-0.02406,-1e-05],"force_p95":0.35489,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.53733,"mean_force":0.50423,"phase_index":1.0,"phase_name":"contact","phase_type":"align","tcp_position_centroid":[0.47223,0.02378,0.07518]},{"body_a":"attachment","body_b":"push_box","contact_count":918.0,"contact_point_centroid":[0.48177,-0.04348,0.04219],"force_p95":12.51765,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.19418,"mean_force":4.42254,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.47275,-0.03148,0.02652]},{"body_a":"world","body_b":"push_box","contact_count":1631.0,"contact_point_centroid":[0.4809,-0.08212,-5e-05],"force_p95":6.70512,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.2376,"mean_force":2.88465,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.47208,-0.0273,0.02693]},{"body_a":"push_box","body_b":"link7","contact_count":36.0,"contact_point_centroid":[0.51229,-0.07755,0.05207],"force_p95":6.70162,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.40569,"mean_force":1.94845,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.47908,-0.06472,0.02432]},{"body_a":"world","body_b":"push_box","contact_count":1915.0,"contact_point_centroid":[0.48708,-0.11129,-1e-05],"force_p95":0.43791,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.67135,"mean_force":0.27982,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.47645,-0.07102,0.04429]},{"body_a":"push_box","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.51159,-0.08494,0.05269],"force_p95":3.10286,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.40291,"mean_force":1.3947,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.48027,-0.07146,0.02382]},{"body_a":"attachment","body_b":"push_box","contact_count":93.0,"contact_point_centroid":[0.49269,-0.08336,0.05045],"force_p95":1.07065,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.33708,"mean_force":0.57895,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.47766,-0.07122,0.02515]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.48794,0.01802,0.20653]}],"total_contact_groups":9},"final_pose_error":0.00943,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48672,-0.10856,0.02499],"final_tcp_position":[0.47647,-0.07101,0.06524],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":48.19194,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.47778,0.03626,0.11564],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10914,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":283.0,"n_steps_budget":630.0,"object_pos_end":[0.47147,-0.02695,0.02468],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12631,"object_to_goal_dist_start":0.12903,"object_z_max":0.02508,"peak_contact_force":0.42886,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1118.0,"raw_peak_contact_force":48.19194,"subtask_id":"contact","tcp_end":[0.4685,0.01026,0.0332],"tcp_start":[0.47778,0.03626,0.11564],"tcp_to_object_dist_end":0.03829,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48869,-0.10802,0.02649],"object_pos_start":[0.47147,-0.02695,0.02468],"object_to_goal_dist_end":0.0435,"object_to_goal_dist_start":0.12631,"object_z_max":0.02649,"peak_contact_force":0.0,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2585.0,"raw_peak_contact_force":20.19418,"subtask_id":"push","tcp_end":[0.48029,-0.07139,0.02385],"tcp_start":[0.4685,0.01026,0.0332],"tcp_to_object_dist_end":0.03767,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.48672,-0.10856,0.02499],"object_pos_start":[0.48869,-0.10802,0.02649],"object_to_goal_dist_end":0.04352,"object_to_goal_dist_start":0.0435,"object_z_max":0.02649,"peak_contact_force":0.24525,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2011.0,"raw_peak_contact_force":3.67135,"tcp_end":[0.47647,-0.07101,0.06524],"tcp_start":[0.48029,-0.07139,0.02385],"tcp_to_object_dist_end":0.05599,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.0679,"average_solve_count":162.0,"average_success_count":162.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.04184,"approach.approach_time":5.47867,"contact.contact_offset_x":-0.00576,"push.push_distance":0.1243,"push.push_speed":0.05,"push.push_time":3.62276,"retract.retract_time":2.38916},"optimized_scores":{"best_composite_score":0.09624,"best_fitness_score":0.50624,"best_task_score":0.65347},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":16.0,"contact_point_centroid":[0.44567,-0.00754,0.03841],"force_p95":35.36634,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.40681,"mean_force":24.22285,"phase_index":1.0,"phase_name":"contact","phase_type":"align","tcp_position_centroid":[0.44411,0.00439,0.03618]},{"body_a":"world","body_b":"push_box","contact_count":1084.0,"contact_point_centroid":[0.45028,-0.03164,-1e-05],"force_p95":0.47127,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.06966,"mean_force":0.59966,"phase_index":1.0,"phase_name":"contact","phase_type":"align","tcp_position_centroid":[0.45266,0.01829,0.07271]},{"body_a":"attachment","body_b":"push_box","contact_count":891.0,"contact_point_centroid":[0.46249,-0.04849,0.04008],"force_p95":11.40653,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.01131,"mean_force":4.00033,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.45459,-0.03645,0.0271]},{"body_a":"world","body_b":"push_box","contact_count":1804.0,"contact_point_centroid":[0.46133,-0.08589,-5e-05],"force_p95":6.22885,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.073,"mean_force":2.30541,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.45424,-0.03538,0.02722]},{"body_a":"world","body_b":"push_box","contact_count":2155.0,"contact_point_centroid":[0.4768,-0.11206,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.94473,"mean_force":0.24683,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.46464,-0.07376,0.04307]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.48238,-0.08649,0.05014],"force_p95":0.37801,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38354,"mean_force":0.33217,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.46826,-0.07418,0.02455]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.48071,0.01598,0.20462]}],"total_contact_groups":7},"final_pose_error":0.00923,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47679,-0.11203,0.02499],"final_tcp_position":[0.46452,-0.07372,0.06616],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":35.40681,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.46319,0.03221,0.11149],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10825,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":274.0,"n_steps_budget":600.0,"object_pos_end":[0.4502,-0.03319,0.02486],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12698,"object_to_goal_dist_start":0.12843,"object_z_max":0.02506,"peak_contact_force":34.20452,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1100.0,"raw_peak_contact_force":35.40681,"subtask_id":"contact","tcp_end":[0.44354,0.00351,0.03329],"tcp_start":[0.46319,0.03221,0.11149],"tcp_to_object_dist_end":0.03825,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47656,-0.11122,0.02513],"object_pos_start":[0.4502,-0.03319,0.02486],"object_to_goal_dist_end":0.04532,"object_to_goal_dist_start":0.12698,"object_z_max":0.02533,"peak_contact_force":0.0,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2695.0,"raw_peak_contact_force":18.01131,"subtask_id":"push","tcp_end":[0.46828,-0.07412,0.02458],"tcp_start":[0.44354,0.00351,0.03329],"tcp_to_object_dist_end":0.03801,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.47679,-0.11203,0.02499],"object_pos_start":[0.47656,-0.11122,0.02513],"object_to_goal_dist_end":0.04451,"object_to_goal_dist_start":0.04532,"object_z_max":0.02513,"peak_contact_force":0.24525,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2158.0,"raw_peak_contact_force":0.94473,"tcp_end":[0.46452,-0.07372,0.06616],"tcp_start":[0.46828,-0.07412,0.02458],"tcp_to_object_dist_end":0.05756,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```