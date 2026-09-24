## Search State

- **Seed**: 1
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 6 | 0.6269 | 0.61 | ❌ rejected |
| 12 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 5 | 0.1058 | 0.53 | ❌ rejected |
| 11 | approach → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | time_limit | time_limit | 7 | -0.0270 | 0.44 | ❌ rejected |
| 10 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 5 | 0.5536 | 0.58 | ❌ rejected |
| 9 | approach → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.3963 | 0.67 | ✅ accepted |

**Proposal policy**: task_score is 0.61 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.627) — your mutation base

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

- **Composite score**: 0.627
- **task_score** (E): 0.612
- **fitness_score**: 0.654  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.2745 |
| contact | 1.00 | 1.00 | 0.0404 |
| push | 1.00 | 1.00 | 0.1404 |
| retract | 1.00 | 1.00 | 0.0410 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.472, 0.072, 0.040) | (0.474, -0.001, 0.025)→(0.474, -0.001, 0.025) | 0.154→0.154 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact | contact | 1.00 / force_exceeded | (0.472, 0.072, 0.040)→(0.474, 0.036, 0.023) | (0.474, -0.001, 0.025)→(0.474, -0.001, 0.025) | 0.154→0.154 | 1.00 / 5.000 | 16.534 | 0.245 |
| push | push | 1.00 / time_limit | (0.474, 0.036, 0.023)→(0.491, -0.102, 0.020) | (0.474, -0.001, 0.025)→(0.458, -0.121, 0.025) | 0.154→0.056 | 1.00 / 1.333 | 0.627 | 24.040 |
| retract | retract | 1.00 / step_budget | (0.491, -0.102, 0.020)→(0.487, -0.101, 0.061) | (0.458, -0.121, 0.025)→(0.456, -0.122, 0.025) | 0.056→0.056 | 1.00 / 4.000 | 0.245 | 7.621 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.911
- lateral_force_integral: None
- approach_alignment: 0.713
- goal_progress: 0.613
- terminal_score: 0.613
- phase_score: 0.796
- phase_breakdown.approach_score: 0.820
- phase_breakdown.push_score: 0.794
- phase_breakdown.contact_score: 0.781

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.723
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.749
- **Median Q (composite search score)**: 0.609
- **K-run variance**: 0.0026
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.312


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.14516,"average_solve_count":186.0,"average_success_count":186.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.03547,"contact.contact_force_threshold":10.44638,"contact.contact_offset_x":0.0071,"push.push_distance":0.18751,"push.push_speed":0.09799,"push.push_timeout":18.89576},"optimized_scores":{"best_composite_score":0.57556,"best_fitness_score":0.60222,"best_task_score":0.74884},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":839.0,"contact_point_centroid":[0.49666,0.00374,0.02216],"force_p95":17.68441,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.23402,"mean_force":4.66421,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49723,0.0156,0.02122]},{"body_a":"world","body_b":"push_box","contact_count":1844.0,"contact_point_centroid":[0.49173,-0.02806,-5e-05],"force_p95":7.27392,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.03894,"mean_force":2.40545,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49724,0.01261,0.02123]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.49274,-0.08057,0.02221],"force_p95":1.96307,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.0735,"mean_force":1.31713,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49637,-0.06931,0.02041]},{"body_a":"world","body_b":"push_box","contact_count":1735.0,"contact_point_centroid":[0.47862,-0.10339,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.19152,"mean_force":0.24836,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49271,-0.06892,0.04105]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49773,0.05863,0.17463]},{"body_a":"world","body_b":"push_box","contact_count":1652.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.4981,0.10349,0.03663]}],"total_contact_groups":6},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47863,-0.10342,0.02499],"final_tcp_position":[0.49249,-0.06882,0.06128],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":24.23402,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.49736,0.11762,0.05195],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.06917,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":413.0,"n_steps_budget":600.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.02499,"peak_contact_force":18.32451,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1652.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.50168,0.09102,0.02611],"tcp_start":[0.49736,0.11762,0.05195],"tcp_to_object_dist_end":0.03698,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47972,-0.10229,0.02505],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.05184,"object_to_goal_dist_start":0.20406,"object_z_max":0.02542,"peak_contact_force":1.57095,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2683.0,"raw_peak_contact_force":24.23402,"subtask_id":"push","tcp_end":[0.49641,-0.06918,0.02044],"tcp_start":[0.50168,0.09102,0.02611],"tcp_to_object_dist_end":0.03737,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":438.0,"n_steps_budget":600.0,"object_pos_end":[0.47863,-0.10342,0.02499],"object_pos_start":[0.47972,-0.10229,0.02505],"object_to_goal_dist_end":0.05125,"object_to_goal_dist_start":0.05184,"object_z_max":0.02508,"peak_contact_force":0.24525,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1738.0,"raw_peak_contact_force":2.0735,"tcp_end":[0.49249,-0.06882,0.06128],"tcp_start":[0.49641,-0.06918,0.02044],"tcp_to_object_dist_end":0.05202,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.13846,"average_solve_count":195.0,"average_success_count":195.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.02867,"contact.contact_force_threshold":5.27127,"contact.contact_offset_x":0.00525,"push.push_distance":0.11743,"push.push_speed":0.08367,"push.push_timeout":10.26864},"optimized_scores":{"best_composite_score":0.69589,"best_fitness_score":0.72255,"best_task_score":0.61302},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":766.0,"contact_point_centroid":[0.47678,-0.05814,0.02187],"force_p95":14.25967,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.97495,"mean_force":3.83879,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.47781,-0.04663,0.0189]},{"body_a":"push_box","body_b":"link7","contact_count":59.0,"contact_point_centroid":[0.49627,-0.01462,0.05003],"force_p95":15.38402,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.73952,"mean_force":6.96256,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.47015,0.00038,0.01858]},{"body_a":"world","body_b":"push_box","contact_count":2009.0,"contact_point_centroid":[0.46456,-0.09123,-5e-05],"force_p95":6.69046,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.14233,"mean_force":1.86248,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.47932,-0.0556,0.01899]},{"body_a":"attachment","body_b":"push_box","contact_count":21.0,"contact_point_centroid":[0.48198,-0.13093,0.02809],"force_p95":3.33834,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.4589,"mean_force":0.92875,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.48803,-0.12099,0.0252]},{"body_a":"world","body_b":"push_box","contact_count":1694.0,"contact_point_centroid":[0.45068,-0.14019,-2e-05],"force_p95":0.42449,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44686,"mean_force":0.25661,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.48681,-0.12062,0.04082]},{"body_a":"world","body_b":"push_box","contact_count":3736.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.48364,0.02604,0.16666]},{"body_a":"world","body_b":"push_box","contact_count":1896.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.46842,0.03236,0.02614]}],"total_contact_groups":7},"final_pose_error":0.00997,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.45109,-0.13996,0.02499],"final_tcp_position":[0.48659,-0.12052,0.06059],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":23.97495,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":934.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3736.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.46887,0.05264,0.03404],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07739,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":474.0,"n_steps_budget":600.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":16.36737,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1896.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.47127,0.01276,0.0219],"tcp_start":[0.46887,0.05264,0.03404],"tcp_to_object_dist_end":0.03707,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45275,-0.13881,0.02503],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.04856,"object_to_goal_dist_start":0.12903,"object_z_max":0.02531,"peak_contact_force":0.24417,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2834.0,"raw_peak_contact_force":23.97495,"subtask_id":"push","tcp_end":[0.49047,-0.12123,0.01974],"tcp_start":[0.47127,0.01276,0.0219],"tcp_to_object_dist_end":0.04195,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":442.0,"n_steps_budget":600.0,"object_pos_end":[0.45109,-0.13996,0.02499],"object_pos_start":[0.45275,-0.13881,0.02503],"object_to_goal_dist_end":0.04993,"object_to_goal_dist_start":0.04856,"object_z_max":0.02513,"peak_contact_force":0.24525,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1715.0,"raw_peak_contact_force":3.4589,"tcp_end":[0.48659,-0.12052,0.06059],"tcp_start":[0.49047,-0.12123,0.01974],"tcp_to_object_dist_end":0.0539,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.13333,"average_solve_count":195.0,"average_success_count":195.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.0268,"contact.contact_force_threshold":2.02688,"contact.contact_offset_x":0.00385,"push.push_distance":0.14671,"push.push_speed":0.07735,"push.push_timeout":15.12325},"optimized_scores":{"best_composite_score":0.6093,"best_fitness_score":0.63597,"best_task_score":0.47504},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":716.0,"contact_point_centroid":[0.46135,-0.05635,0.02208],"force_p95":13.69609,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.90981,"mean_force":3.66614,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.46262,-0.04503,0.01911]},{"body_a":"push_box","body_b":"link7","contact_count":25.0,"contact_point_centroid":[0.47583,-0.02109,0.05006],"force_p95":16.02058,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.04784,"mean_force":4.90488,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.44942,-0.00418,0.01918]},{"body_a":"attachment","body_b":"push_box","contact_count":49.0,"contact_point_centroid":[0.47439,-0.1213,0.02953],"force_p95":2.54662,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.33066,"mean_force":1.15178,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.48306,-0.11432,0.02524]},{"body_a":"world","body_b":"push_box","contact_count":2281.0,"contact_point_centroid":[0.44618,-0.08896,-4e-05],"force_p95":4.82547,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.32326,"mean_force":1.45782,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.46675,-0.05754,0.01915]},{"body_a":"world","body_b":"push_box","contact_count":1594.0,"contact_point_centroid":[0.43792,-0.12229,-2e-05],"force_p95":0.38733,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.91549,"mean_force":0.27348,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.48199,-0.114,0.0411]},{"body_a":"world","body_b":"push_box","contact_count":3712.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.47374,0.02259,0.16679]},{"body_a":"world","body_b":"push_box","contact_count":1896.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.44747,0.02515,0.02666]}],"total_contact_groups":7},"final_pose_error":0.00995,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.43848,-0.12241,0.02499],"final_tcp_position":[0.48182,-0.11393,0.06021],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":23.90981,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":928.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3712.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.4489,0.04564,0.03445],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07781,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":474.0,"n_steps_budget":600.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":14.90873,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1896.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.44926,0.00539,0.0223],"tcp_start":[0.4489,0.04564,0.03445],"tcp_to_object_dist_end":0.03709,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.44063,-0.12091,0.025],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.06611,"object_to_goal_dist_start":0.12843,"object_z_max":0.02518,"peak_contact_force":0.0659,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3022.0,"raw_peak_contact_force":23.90981,"subtask_id":"push","tcp_end":[0.48568,-0.1146,0.01936],"tcp_start":[0.44926,0.00539,0.0223],"tcp_to_object_dist_end":0.04584,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":430.0,"n_steps_budget":600.0,"object_pos_end":[0.43848,-0.12241,0.02499],"object_pos_start":[0.44063,-0.12091,0.025],"object_to_goal_dist_end":0.06742,"object_to_goal_dist_start":0.06611,"object_z_max":0.02561,"peak_contact_force":0.24525,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1643.0,"raw_peak_contact_force":17.33066,"tcp_end":[0.48182,-0.11393,0.06021],"tcp_start":[0.48568,-0.1146,0.01936],"tcp_to_object_dist_end":0.05648,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```