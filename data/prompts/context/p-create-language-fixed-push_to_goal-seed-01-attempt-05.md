## Search State

- **Seed**: 1
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.7337 | 0.91 | ❌ rejected |
| 4 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | time_limit | force_exceeded | time_limit | time_limit | 7 | 1.0376 | 0.52 | ❌ rejected |
| 3 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.6732 | 0.92 | ❌ rejected |
| 2 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.5377 | 0.89 | ❌ rejected |
| 1 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.7411 | 0.95 | ✅ accepted |

**Proposal policy**: task_score is near-perfect (0.91). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

## Current Skill (Q=0.734) — your mutation base

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

- **Composite score**: 0.734
- **task_score** (E): 0.908
- **fitness_score**: 0.794  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2821 |
| contact_1 | 1.00 | 1.00 | 0.0406 |
| push_1 | 1.00 | 1.00 | 0.1445 |
| retract_1 | 1.00 | 1.00 | 0.2505 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.472, 0.075, 0.033) | (0.474, -0.001, 0.025)→(0.474, -0.001, 0.025) | 0.154→0.154 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / force_exceeded | (0.472, 0.075, 0.033)→(0.470, 0.036, 0.022) | (0.474, -0.001, 0.025)→(0.474, -0.001, 0.025) | 0.154→0.154 | 1.00 / 5.000 | 27.804 | 0.245 |
| push_1 | push | 1.00 / step_budget | (0.470, 0.036, 0.022)→(0.494, -0.104, 0.020) | (0.474, -0.001, 0.025)→(0.513, -0.137, 0.025) | 0.154→0.018 | 1.00 / 2.000 | 1.041 | 43.699 |
| retract_1 | retract | 1.00 / step_budget | (0.494, -0.104, 0.020)→(0.494, -0.104, 0.271) | (0.513, -0.137, 0.025)→(0.515, -0.143, 0.025) | 0.018→0.017 | 1.00 / 4.000 | 0.245 | 4.541 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.988
- lateral_force_integral: None
- approach_alignment: 0.964
- goal_progress: 0.986
- terminal_score: 0.986
- phase_score: 0.756
- phase_breakdown.push_score: 0.721
- phase_breakdown.approach_score: 0.819
- phase_breakdown.contact_score: 0.771

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.848
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.986
- **Median Q (composite search score)**: 0.761
- **K-run variance**: 0.0034
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.476


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.44488,"average_solve_count":254.0,"average_success_count":254.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":8.61887,"contact_1.speed":0.04971,"push_1.push_depth":0.00028,"push_1.push_speed":0.03867,"push_1.push_tolerance":0.02765},"optimized_scores":{"best_composite_score":0.6522,"best_fitness_score":0.7122,"best_task_score":0.79798},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":251.0,"contact_point_centroid":[0.50147,-0.00073,0.03964],"force_p95":34.83705,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":67.99946,"mean_force":5.34767,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49522,0.0108,0.01901]},{"body_a":"push_box","body_b":"link7","contact_count":36.0,"contact_point_centroid":[0.53268,-0.05228,0.05217],"force_p95":50.77531,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":54.27269,"mean_force":15.09061,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49567,-0.04691,0.01924]},{"body_a":"world","body_b":"push_box","contact_count":339.0,"contact_point_centroid":[0.51473,-0.04916,-0.00012],"force_p95":27.20296,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":38.37346,"mean_force":6.07701,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49553,-0.00286,0.01931]},{"body_a":"world","body_b":"push_box","contact_count":954.0,"contact_point_centroid":[0.53843,-0.13494,-7e-05],"force_p95":0.52676,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.82486,"mean_force":0.29034,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49549,-0.09313,0.15802]},{"body_a":"world","body_b":"push_box","contact_count":3980.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49785,0.06389,0.16385]},{"body_a":"world","body_b":"push_box","contact_count":1828.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49549,0.10863,0.02431]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.51006,-0.10329,0.05111],"force_p95":0.10331,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10875,"mean_force":0.05438,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49663,-0.09329,0.02012]}],"total_contact_groups":7},"final_pose_error":0.04938,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53861,-0.13554,0.02499],"final_tcp_position":[0.49666,-0.09314,0.27074],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":67.99946,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":995.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3980.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.49751,0.12763,0.03133],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07395,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":457.0,"n_steps_budget":600.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.02499,"peak_contact_force":29.49103,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1828.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.49665,0.09103,0.02131],"tcp_start":[0.49751,0.12763,0.03133],"tcp_to_object_dist_end":0.03746,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":356.0,"n_steps_budget":1000.0,"object_pos_end":[0.53086,-0.11897,0.02561],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.04377,"object_to_goal_dist_start":0.20406,"object_z_max":0.02664,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":626.0,"raw_peak_contact_force":67.99946,"subtask_id":"push","tcp_end":[0.49663,-0.0931,0.02012],"tcp_start":[0.49665,0.09103,0.02131],"tcp_to_object_dist_end":0.04326,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":279.0,"n_steps_budget":1000.0,"object_pos_end":[0.53861,-0.13554,0.02499],"object_pos_start":[0.53086,-0.11897,0.02561],"object_to_goal_dist_end":0.04123,"object_to_goal_dist_start":0.04377,"object_z_max":0.02807,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":956.0,"raw_peak_contact_force":2.82486,"tcp_end":[0.49666,-0.09314,0.27074],"tcp_start":[0.49663,-0.0931,0.02012],"tcp_to_object_dist_end":0.25288,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.48636,"average_solve_count":220.0,"average_success_count":220.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":1.00182,"contact_1.speed":0.03709,"push_1.push_depth":0.00031,"push_1.push_speed":0.03666,"push_1.push_tolerance":0.01205},"optimized_scores":{"best_composite_score":0.78789,"best_fitness_score":0.84789,"best_task_score":0.98588},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":603.0,"contact_point_centroid":[0.48321,-0.0626,0.03463],"force_p95":17.83741,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.62973,"mean_force":3.92931,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47959,-0.05069,0.01961]},{"body_a":"world","body_b":"push_box","contact_count":848.0,"contact_point_centroid":[0.48439,-0.1016,-4e-05],"force_p95":9.8319,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.54056,"mean_force":3.17764,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47908,-0.04831,0.01966]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.50112,-0.12263,0.0502],"force_p95":8.3769,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.3769,"mean_force":8.3769,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.494,-0.11063,0.02006]},{"body_a":"world","body_b":"push_box","contact_count":1093.0,"contact_point_centroid":[0.50056,-0.14865,-2e-05],"force_p95":0.26162,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.14653,"mean_force":0.25878,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49266,-0.11047,0.14252]},{"body_a":"world","body_b":"push_box","contact_count":3432.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48376,0.02618,0.16621]},{"body_a":"world","body_b":"push_box","contact_count":2492.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4666,0.03172,0.02628]}],"total_contact_groups":6},"final_pose_error":0.04974,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50057,-0.14827,0.02499],"final_tcp_position":[0.49404,-0.11059,0.27032],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":30.62973,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":858.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3432.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.46921,0.05269,0.0342],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07745,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":623.0,"n_steps_budget":810.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":24.04332,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2492.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.4672,0.0128,0.02227],"tcp_start":[0.46921,0.05269,0.0342],"tcp_to_object_dist_end":0.03732,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":679.0,"n_steps_budget":1000.0,"object_pos_end":[0.50031,-0.14748,0.02504],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.00254,"object_to_goal_dist_start":0.12903,"object_z_max":0.0254,"peak_contact_force":1.52165,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1451.0,"raw_peak_contact_force":30.62973,"subtask_id":"push","tcp_end":[0.494,-0.11063,0.02006],"tcp_start":[0.4672,0.0128,0.02227],"tcp_to_object_dist_end":0.03772,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":279.0,"n_steps_budget":1000.0,"object_pos_end":[0.50057,-0.14827,0.02499],"object_pos_start":[0.50031,-0.14748,0.02504],"object_to_goal_dist_end":0.00182,"object_to_goal_dist_start":0.00254,"object_z_max":0.02519,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1094.0,"raw_peak_contact_force":8.3769,"tcp_end":[0.49404,-0.11059,0.27032],"tcp_start":[0.494,-0.11063,0.02006],"tcp_to_object_dist_end":0.24829,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.57068,"average_solve_count":191.0,"average_success_count":191.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":2.58658,"contact_1.speed":0.04311,"push_1.push_depth":0.00289,"push_1.push_speed":0.05646,"push_1.push_tolerance":0.0119},"optimized_scores":{"best_composite_score":0.76114,"best_fitness_score":0.82114,"best_task_score":0.94065},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":566.0,"contact_point_centroid":[0.47317,-0.06456,0.04074],"force_p95":17.49817,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.46719,"mean_force":5.14696,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46819,-0.05264,0.01999]},{"body_a":"world","body_b":"push_box","contact_count":910.0,"contact_point_centroid":[0.47845,-0.10323,-5e-05],"force_p95":9.44922,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.60277,"mean_force":3.63473,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46723,-0.05023,0.02004]},{"body_a":"world","body_b":"push_box","contact_count":1077.0,"contact_point_centroid":[0.50646,-0.14637,-2e-05],"force_p95":0.25334,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.4212,"mean_force":0.25642,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49075,-0.10881,0.14475]},{"body_a":"attachment","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.4995,-0.121,0.05053],"force_p95":1.5224,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.67227,"mean_force":0.84795,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49202,-0.10909,0.02025]},{"body_a":"world","body_b":"push_box","contact_count":3420.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47382,0.02272,0.16631]},{"body_a":"world","body_b":"push_box","contact_count":2244.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4463,0.0247,0.02683]}],"total_contact_groups":6},"final_pose_error":0.04935,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50639,-0.14585,0.02499],"final_tcp_position":[0.4921,-0.10895,0.2709],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":32.46719,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":855.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3420.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.44924,0.04571,0.0345],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07788,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":561.0,"n_steps_budget":720.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":29.87687,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2244.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.44642,0.00541,0.02266],"tcp_start":[0.44924,0.04571,0.0345],"tcp_to_object_dist_end":0.03726,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":689.0,"n_steps_budget":1000.0,"object_pos_end":[0.50698,-0.14502,0.02523],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.00858,"object_to_goal_dist_start":0.12843,"object_z_max":0.02542,"peak_contact_force":1.60148,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1476.0,"raw_peak_contact_force":32.46719,"subtask_id":"push","tcp_end":[0.49204,-0.10898,0.02025],"tcp_start":[0.44642,0.00541,0.02266],"tcp_to_object_dist_end":0.03933,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":279.0,"n_steps_budget":1000.0,"object_pos_end":[0.50639,-0.14585,0.02499],"object_pos_start":[0.50698,-0.14502,0.02523],"object_to_goal_dist_end":0.00762,"object_to_goal_dist_start":0.00858,"object_z_max":0.02542,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1081.0,"raw_peak_contact_force":2.4212,"tcp_end":[0.4921,-0.10895,0.2709],"tcp_start":[0.49204,-0.10898,0.02025],"tcp_to_object_dist_end":0.24907,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```