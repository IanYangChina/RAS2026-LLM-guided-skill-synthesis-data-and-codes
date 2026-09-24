## Search State

- **Seed**: 1
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.6732 | 0.92 | ❌ rejected |
| 2 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.5377 | 0.89 | ❌ rejected |
| 1 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.7411 | 0.95 | ✅ accepted |
| 0 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 2 | 0.8865 | 0.91 | ✅ accepted |

**Proposal policy**: task_score is near-perfect (0.92). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

## Current Skill (Q=0.673) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: push_box
    offset:
    - 0.0
    - 0.08
    - 0.0
    orientation:
      mode: keep_current
  subtask_id: approach
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: push_box
    offset:
    - 0.0
    - 0.03
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.01
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: contact
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: goal_marker
    offset:
    - 0.0
    - 0.03
    - 0.0
    offset_along_axis:
      distance: 0.0
      axis: task_goal_direction
      mode: add_to_offset
      sign: negative
    orientation:
      mode: keep_current
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.0
      - 0.06
      default: 0.0
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.06
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
    push_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: push
- id: retract_1
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
    - 0.3
    tolerance: 0.05
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.08, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.03, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_goal, entity=goal_marker, offset=[0.0, 0.03, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.0, mode=add_to_offset, sign=negative}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.3], tolerance=0.05
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.673
- **task_score** (E): 0.920
- **fitness_score**: 0.817  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2821 |
| contact_1 | 1.00 | 1.00 | 0.0421 |
| push_1 | 1.00 | 1.00 | 0.1469 |
| retract_1 | 1.00 | 1.00 | 0.2502 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.472, 0.075, 0.033) | (0.474, -0.001, 0.025)→(0.474, -0.001, 0.025) | 0.154→0.154 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / force_exceeded | (0.472, 0.075, 0.033)→(0.470, 0.035, 0.022) | (0.474, -0.001, 0.025)→(0.475, -0.002, 0.025) | 0.154→0.152 | 1.00 / 4.333 | 19.198 | 2.499 |
| push_1 | push | 1.00 / step_budget | (0.470, 0.035, 0.022)→(0.495, -0.108, 0.021) | (0.475, -0.002, 0.025)→(0.513, -0.140, 0.027) | 0.152→0.017 | 1.00 / 3.000 | 16.009 | 38.366 |
| retract_1 | retract | 1.00 / step_budget | (0.495, -0.108, 0.021)→(0.495, -0.108, 0.271) | (0.513, -0.140, 0.027)→(0.512, -0.142, 0.025) | 0.017→0.015 | 1.00 / 4.000 | 0.245 | 13.859 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.994
- lateral_force_integral: None
- approach_alignment: 0.933
- goal_progress: 0.993
- terminal_score: 0.993
- phase_score: 0.763
- phase_breakdown.push_score: 0.734
- phase_breakdown.approach_score: 0.820
- phase_breakdown.contact_score: 0.774

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.855
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.993
- **Median Q (composite search score)**: 0.686
- **K-run variance**: 0.0110
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.413


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.43411,"average_solve_count":258.0,"average_success_count":258.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":5.81389,"contact_1.speed":0.03609,"push_1.push_depth":0.00402,"push_1.push_speed":0.03824,"push_1.push_tolerance":0.0162},"optimized_scores":{"best_composite_score":0.68556,"best_fitness_score":0.74556,"best_task_score":0.8186},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":348.0,"contact_point_centroid":[0.53084,-0.06311,0.05447],"force_p95":38.59263,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":56.10495,"mean_force":21.5751,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49666,-0.05565,0.02067]},{"body_a":"attachment","body_b":"push_box","contact_count":594.0,"contact_point_centroid":[0.50745,-0.02194,0.04596],"force_p95":49.11677,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":53.6334,"mean_force":17.47934,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49568,-0.01333,0.01975]},{"body_a":"world","body_b":"push_box","contact_count":848.0,"contact_point_centroid":[0.52872,-0.06456,-8e-05],"force_p95":41.69556,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.41499,"mean_force":18.03195,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4959,-0.01935,0.01997]},{"body_a":"push_box","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.53537,-0.09986,0.05526],"force_p95":29.29956,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.02262,"mean_force":11.87337,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49792,-0.10056,0.02213]},{"body_a":"world","body_b":"push_box","contact_count":998.0,"contact_point_centroid":[0.53099,-0.1277,-5e-05],"force_p95":0.5806,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.70653,"mean_force":0.31586,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49704,-0.10016,0.1547]},{"body_a":"attachment","body_b":"push_box","contact_count":15.0,"contact_point_centroid":[0.51541,-0.10217,0.05731],"force_p95":17.20572,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.36472,"mean_force":4.52641,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4968,-0.1005,0.02728]},{"body_a":"world","body_b":"push_box","contact_count":3980.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49785,0.06389,0.16385]},{"body_a":"world","body_b":"push_box","contact_count":2336.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49544,0.10817,0.02414]}],"total_contact_groups":8},"final_pose_error":0.04993,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5294,-0.12751,0.02499],"final_tcp_position":[0.49826,-0.10026,0.27211],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":56.10495,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":995.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3980.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.49751,0.12763,0.03133],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07395,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":584.0,"n_steps_budget":780.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.02499,"peak_contact_force":26.29399,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2336.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.49665,0.09104,0.02131],"tcp_start":[0.49751,0.12763,0.03133],"tcp_to_object_dist_end":0.03747,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":689.0,"n_steps_budget":1000.0,"object_pos_end":[0.53277,-0.12438,0.02959],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.04185,"object_to_goal_dist_start":0.20406,"object_z_max":0.02967,"peak_contact_force":35.98462,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1790.0,"raw_peak_contact_force":56.10495,"subtask_id":"push","tcp_end":[0.49825,-0.10022,0.02204],"tcp_start":[0.49665,0.09104,0.02131],"tcp_to_object_dist_end":0.04281,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":279.0,"n_steps_budget":1000.0,"object_pos_end":[0.5294,-0.12751,0.02499],"object_pos_start":[0.53277,-0.12438,0.02959],"object_to_goal_dist_end":0.03702,"object_to_goal_dist_start":0.04185,"object_z_max":0.02965,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1020.0,"raw_peak_contact_force":33.02262,"tcp_end":[0.49826,-0.10026,0.27211],"tcp_start":[0.49825,-0.10022,0.02204],"tcp_to_object_dist_end":0.25056,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.37931,"average_solve_count":232.0,"average_success_count":232.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":17.9135,"contact_1.speed":0.02551,"push_1.push_depth":0.00073,"push_1.push_speed":0.03621,"push_1.push_tolerance":0.01056},"optimized_scores":{"best_composite_score":0.53936,"best_fitness_score":0.84936,"best_task_score":0.94952},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":721.0,"contact_point_centroid":[0.48455,-0.06543,0.03601],"force_p95":14.67551,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.55522,"mean_force":3.79975,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47976,-0.05355,0.0191]},{"body_a":"world","body_b":"push_box","contact_count":953.0,"contact_point_centroid":[0.49031,-0.11274,-4e-05],"force_p95":8.59133,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.53044,"mean_force":3.30649,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47969,-0.05308,0.01915]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.50038,-0.12381,0.04078],"force_p95":7.24232,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.88102,"mean_force":3.28346,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49423,-0.11194,0.02004]},{"body_a":"attachment","body_b":"push_box","contact_count":112.0,"contact_point_centroid":[0.47024,-0.00135,0.03486],"force_p95":5.31185,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.00557,"mean_force":2.3196,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46734,0.0106,0.02185]},{"body_a":"world","body_b":"push_box","contact_count":1081.0,"contact_point_centroid":[0.50635,-0.1487,-3e-05],"force_p95":0.25483,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.95492,"mean_force":0.26256,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49291,-0.11167,0.14383]},{"body_a":"world","body_b":"push_box","contact_count":3764.0,"contact_point_centroid":[0.47166,-0.02514,-1e-05],"force_p95":0.33252,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.92848,"mean_force":0.31613,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46659,0.02992,0.02584]},{"body_a":"world","body_b":"push_box","contact_count":3432.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48376,0.02618,0.16621]}],"total_contact_groups":7},"final_pose_error":0.04975,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50626,-0.14819,0.02499],"final_tcp_position":[0.49429,-0.11182,0.2703],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":26.55522,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":858.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3432.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.46921,0.05269,0.0342],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07745,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47206,-0.02857,0.02502],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12461,"object_to_goal_dist_start":0.12903,"object_z_max":0.02507,"peak_contact_force":3.52451,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3876.0,"raw_peak_contact_force":7.00557,"subtask_id":"contact","tcp_end":[0.46745,0.00831,0.02139],"tcp_start":[0.46921,0.05269,0.0342],"tcp_to_object_dist_end":0.03734,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":815.0,"n_steps_budget":1000.0,"object_pos_end":[0.50642,-0.14769,0.02561],"object_pos_start":[0.47206,-0.02857,0.02502],"object_to_goal_dist_end":0.00685,"object_to_goal_dist_start":0.12461,"object_z_max":0.02594,"peak_contact_force":9.77113,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1674.0,"raw_peak_contact_force":26.55522,"subtask_id":"push","tcp_end":[0.49426,-0.11186,0.02005],"tcp_start":[0.46745,0.00831,0.02139],"tcp_to_object_dist_end":0.03825,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":279.0,"n_steps_budget":1000.0,"object_pos_end":[0.50626,-0.14819,0.02499],"object_pos_start":[0.50642,-0.14769,0.02561],"object_to_goal_dist_end":0.00651,"object_to_goal_dist_start":0.00685,"object_z_max":0.02571,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1084.0,"raw_peak_contact_force":7.88102,"tcp_end":[0.49429,-0.11182,0.2703],"tcp_start":[0.49426,-0.11186,0.02005],"tcp_to_object_dist_end":0.24828,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.57368,"average_solve_count":190.0,"average_success_count":190.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":18.75298,"contact_1.speed":0.04702,"push_1.push_depth":0.0009,"push_1.push_speed":0.05536,"push_1.push_tolerance":0.01087},"optimized_scores":{"best_composite_score":0.79482,"best_fitness_score":0.85482,"best_task_score":0.99259},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":715.0,"contact_point_centroid":[0.47245,-0.06713,0.03416],"force_p95":16.34486,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.43761,"mean_force":4.13504,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46917,-0.0552,0.01993]},{"body_a":"world","body_b":"push_box","contact_count":1272.0,"contact_point_centroid":[0.47453,-0.10382,-4e-05],"force_p95":8.35382,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.68911,"mean_force":2.65914,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46972,-0.05646,0.01996]},{"body_a":"world","body_b":"push_box","contact_count":1112.0,"contact_point_centroid":[0.49907,-0.14953,-2e-05],"force_p95":0.24575,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.67324,"mean_force":0.24761,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49185,-0.11178,0.14057]},{"body_a":"world","body_b":"push_box","contact_count":3420.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47382,0.02272,0.16631]},{"body_a":"world","body_b":"push_box","contact_count":2064.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44632,0.0249,0.02689]}],"total_contact_groups":5},"final_pose_error":0.04971,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49917,-0.14954,0.02499],"final_tcp_position":[0.49321,-0.11192,0.27048],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":32.43761,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":855.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3420.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.44924,0.04571,0.0345],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07788,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":516.0,"n_steps_budget":660.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":27.77444,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2064.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.44643,0.0054,0.02265],"tcp_start":[0.44924,0.04571,0.0345],"tcp_to_object_dist_end":0.03725,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":812.0,"n_steps_budget":1000.0,"object_pos_end":[0.49872,-0.14901,0.02498],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.00162,"object_to_goal_dist_start":0.12843,"object_z_max":0.02538,"peak_contact_force":2.27248,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1987.0,"raw_peak_contact_force":32.43761,"subtask_id":"push","tcp_end":[0.49317,-0.11195,0.02019],"tcp_start":[0.44643,0.0054,0.02265],"tcp_to_object_dist_end":0.03778,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":279.0,"n_steps_budget":1000.0,"object_pos_end":[0.49917,-0.14954,0.02499],"object_pos_start":[0.49872,-0.14901,0.02498],"object_to_goal_dist_end":0.00095,"object_to_goal_dist_start":0.00162,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1112.0,"raw_peak_contact_force":0.67324,"tcp_end":[0.49321,-0.11192,0.27048],"tcp_start":[0.49317,-0.11195,0.02019],"tcp_to_object_dist_end":0.24843,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```