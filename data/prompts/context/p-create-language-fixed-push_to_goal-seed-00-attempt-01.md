## Search State

- **Seed**: 0
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 2 | 0.8793 | 0.85 | ✅ accepted |
| 0 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 2 | 0.8232 | 0.76 | ✅ accepted |

**Proposal policy**: task_score is 0.85 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.879) — your mutation base

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
    - 0.08
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.02
      - 0.18
      default: 0.08
      binds_to:
      - path: target.offset.y
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
    - 0.05
    - 0.1
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
- **push_1** (`push`)
  - target: source=yaml, anchor=task_goal, entity=goal_marker, offset=[0.0, 0.08, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_depth: status=consumed; consumers=target.offset.y (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.05, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.879
- **task_score** (E): 0.847
- **fitness_score**: 0.789  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.160

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2812 |
| contact_1 | 1.00 | 1.00 | 0.0405 |
| push_1 | 1.00 | 1.00 | 0.1466 |
| retract_1 | 1.00 | 1.00 | 0.1014 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.493, 0.077, 0.033) | (0.496, 0.001, 0.025)→(0.496, 0.001, 0.025) | 0.152→0.152 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / force_exceeded | (0.493, 0.077, 0.033)→(0.492, 0.038, 0.022) | (0.496, 0.001, 0.025)→(0.496, 0.001, 0.025) | 0.152→0.152 | 1.00 / 5.000 | 27.512 | 0.245 |
| push_1 | push | 1.00 / step_budget | (0.492, 0.038, 0.022)→(0.497, -0.108, 0.021) | (0.496, 0.001, 0.025)→(0.519, -0.138, 0.028) | 0.152→0.027 | 1.00 / 4.000 | 23.699 | 43.212 |
| retract_1 | retract | 1.00 / step_budget | (0.497, -0.108, 0.021)→(0.494, -0.060, 0.111) | (0.519, -0.138, 0.028)→(0.517, -0.138, 0.025) | 0.027→0.025 | 1.00 / 4.000 | 0.245 | 26.877 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.664
- goal_progress: 0.960
- terminal_score: 0.960
- phase_score: 0.803
- phase_breakdown.push_score: 0.816
- phase_breakdown.contact_score: 0.771
- phase_breakdown.approach_score: 0.819

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.866
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.960
- **Median Q (composite search score)**: 0.908
- **K-run variance**: 0.0059
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 11.0
- **Parameters at upper bound**: contact_1.contact_force
- **Final σ (mean)**: 0.383


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.76923,"average_solve_count":130.0,"average_success_count":130.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":17.77317,"push_1.push_depth":0.02182},"optimized_scores":{"best_composite_score":0.90826,"best_fitness_score":0.81826,"best_task_score":0.81254},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":442.0,"contact_point_centroid":[0.53362,-0.09008,0.05397],"force_p95":31.90877,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.70013,"mean_force":16.83226,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50096,-0.08021,0.01992]},{"body_a":"attachment","body_b":"push_box","contact_count":636.0,"contact_point_centroid":[0.51408,-0.07052,0.04723],"force_p95":28.23147,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.27662,"mean_force":11.82466,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50256,-0.06079,0.01943]},{"body_a":"push_box","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.53528,-0.12476,0.05497],"force_p95":32.62226,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.32362,"mean_force":11.55182,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49844,-0.11825,0.02176]},{"body_a":"world","body_b":"push_box","contact_count":1042.0,"contact_point_centroid":[0.5311,-0.11144,-7e-05],"force_p95":27.84028,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.20749,"mean_force":12.77713,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50257,-0.06175,0.01955]},{"body_a":"world","body_b":"push_box","contact_count":2334.0,"contact_point_centroid":[0.52419,-0.14761,-1e-05],"force_p95":0.41094,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.68044,"mean_force":0.28729,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49511,-0.09182,0.06875]},{"body_a":"attachment","body_b":"push_box","contact_count":44.0,"contact_point_centroid":[0.5142,-0.12002,0.05477],"force_p95":11.37223,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.5312,"mean_force":1.68587,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49672,-0.11481,0.026]},{"body_a":"world","body_b":"push_box","contact_count":3496.0,"contact_point_centroid":[0.51644,-0.02763,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50494,0.02455,0.16585]},{"body_a":"world","body_b":"push_box","contact_count":1896.0,"contact_point_centroid":[0.51644,-0.02763,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50996,0.02902,0.02519]}],"total_contact_groups":8},"final_pose_error":0.01136,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52294,-0.14691,0.02499],"final_tcp_position":[0.4953,-0.07066,0.11112],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51644,-0.02763,0.025]},"peak_contact_force":41.70013,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":874.0,"n_steps_budget":1000.0,"object_pos_end":[0.51644,-0.02763,0.02499],"object_pos_start":[0.51644,-0.02763,0.025],"object_to_goal_dist_end":0.12347,"object_to_goal_dist_start":0.12347,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3496.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.51171,0.04945,0.03319],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07766,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":474.0,"n_steps_budget":600.0,"object_pos_end":[0.51644,-0.02763,0.02499],"object_pos_start":[0.51644,-0.02763,0.02499],"object_to_goal_dist_end":0.12347,"object_to_goal_dist_start":0.12347,"object_z_max":0.02499,"peak_contact_force":26.84816,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1896.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.51153,0.00931,0.02129],"tcp_start":[0.51171,0.04945,0.03319],"tcp_to_object_dist_end":0.03745,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":733.0,"n_steps_budget":870.0,"object_pos_end":[0.52644,-0.14792,0.02925],"object_pos_start":[0.51644,-0.02763,0.02499],"object_to_goal_dist_end":0.02687,"object_to_goal_dist_start":0.12347,"object_z_max":0.02925,"peak_contact_force":27.2763,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2120.0,"raw_peak_contact_force":41.70013,"subtask_id":"push","tcp_end":[0.49869,-0.11818,0.02168],"tcp_start":[0.51153,0.00931,0.02129],"tcp_to_object_dist_end":0.04138,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.52294,-0.14691,0.02499],"object_pos_start":[0.52644,-0.14792,0.02925],"object_to_goal_dist_end":0.02315,"object_to_goal_dist_start":0.02687,"object_z_max":0.02928,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2385.0,"raw_peak_contact_force":36.32362,"tcp_end":[0.4953,-0.07066,0.11112],"tcp_start":[0.49869,-0.11818,0.02168],"tcp_to_object_dist_end":0.11831,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.7931,"average_solve_count":145.0,"average_success_count":145.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":19.99977,"push_1.push_depth":0.04188},"optimized_scores":{"best_composite_score":0.77379,"best_fitness_score":0.68379,"best_task_score":0.76996},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":629.0,"contact_point_centroid":[0.52912,-0.04161,0.05424],"force_p95":34.69741,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.66792,"mean_force":18.47087,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49601,-0.03263,0.0202]},{"body_a":"attachment","body_b":"push_box","contact_count":870.0,"contact_point_centroid":[0.50842,-0.01593,0.04881],"force_p95":35.27006,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.99568,"mean_force":16.10379,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49547,-0.00736,0.01967]},{"body_a":"world","body_b":"push_box","contact_count":1425.0,"contact_point_centroid":[0.5285,-0.05607,-7e-05],"force_p95":31.30877,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":41.66032,"mean_force":15.23725,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49561,-0.00961,0.01981]},{"body_a":"push_box","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.53531,-0.08822,0.05513],"force_p95":30.79544,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.51225,"mean_force":11.42561,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49764,-0.08701,0.02204]},{"body_a":"attachment","body_b":"push_box","contact_count":59.0,"contact_point_centroid":[0.51357,-0.08547,0.05501],"force_p95":4.17632,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.49912,"mean_force":1.45424,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49565,-0.08257,0.02794]},{"body_a":"world","body_b":"push_box","contact_count":2267.0,"contact_point_centroid":[0.5286,-0.11195,-2e-05],"force_p95":0.52203,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.57036,"mean_force":0.29757,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49436,-0.06026,0.07006]},{"body_a":"world","body_b":"push_box","contact_count":3980.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49785,0.06389,0.16385]},{"body_a":"world","body_b":"push_box","contact_count":1828.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49549,0.10863,0.02431]}],"total_contact_groups":8},"final_pose_error":0.01132,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5268,-0.11146,0.02499],"final_tcp_position":[0.49457,-0.03959,0.11144],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":49.66792,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":995.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3980.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.49751,0.12763,0.03133],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07395,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":457.0,"n_steps_budget":600.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.02499,"peak_contact_force":29.49103,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1828.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.49665,0.09103,0.02131],"tcp_start":[0.49751,0.12763,0.03133],"tcp_to_object_dist_end":0.03746,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53096,-0.11252,0.02943],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.04882,"object_to_goal_dist_start":0.20406,"object_z_max":0.02945,"peak_contact_force":34.17354,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2924.0,"raw_peak_contact_force":49.66792,"subtask_id":"push","tcp_end":[0.49794,-0.08691,0.02191],"tcp_start":[0.49665,0.09103,0.02131],"tcp_to_object_dist_end":0.04245,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.5268,-0.11146,0.02499],"object_pos_start":[0.53096,-0.11252,0.02943],"object_to_goal_dist_end":0.04694,"object_to_goal_dist_start":0.04882,"object_z_max":0.0295,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2334.0,"raw_peak_contact_force":32.51225,"tcp_end":[0.49457,-0.03959,0.11144],"tcp_start":[0.49794,-0.08691,0.02191],"tcp_to_object_dist_end":0.11696,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.77099,"average_solve_count":131.0,"average_success_count":131.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":7.75978,"push_1.push_depth":0.02464},"optimized_scores":{"best_composite_score":0.95579,"best_fitness_score":0.86579,"best_task_score":0.95956},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":679.0,"contact_point_centroid":[0.48337,-0.06575,0.03421],"force_p95":15.5365,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.2682,"mean_force":4.1854,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47966,-0.05385,0.01955]},{"body_a":"world","body_b":"push_box","contact_count":990.0,"contact_point_centroid":[0.48508,-0.10732,-4e-05],"force_p95":8.86131,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.14521,"mean_force":3.266,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47911,-0.05117,0.01961]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.50144,-0.12999,0.05003],"force_p95":10.80795,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.79543,"mean_force":5.1262,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49452,-0.11804,0.02007]},{"body_a":"world","body_b":"push_box","contact_count":2497.0,"contact_point_centroid":[0.50069,-0.15546,-1e-05],"force_p95":0.24536,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.49583,"mean_force":0.25441,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49106,-0.09304,0.06452]},{"body_a":"world","body_b":"push_box","contact_count":3432.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48376,0.02618,0.16621]},{"body_a":"world","body_b":"push_box","contact_count":1884.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46666,0.03231,0.02648]}],"total_contact_groups":6},"final_pose_error":0.01128,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50068,-0.15517,0.02499],"final_tcp_position":[0.49117,-0.07045,0.10961],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":38.2682,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":858.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3432.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.46921,0.05269,0.0342],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07745,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":471.0,"n_steps_budget":600.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":26.19751,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1884.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.4672,0.0128,0.02227],"tcp_start":[0.46921,0.05269,0.0342],"tcp_to_object_dist_end":0.03731,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":791.0,"n_steps_budget":900.0,"object_pos_end":[0.50077,-0.15476,0.02493],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.00482,"object_to_goal_dist_start":0.12903,"object_z_max":0.02546,"peak_contact_force":9.64659,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1669.0,"raw_peak_contact_force":38.2682,"subtask_id":"push","tcp_end":[0.49454,-0.11797,0.02008],"tcp_start":[0.4672,0.0128,0.02227],"tcp_to_object_dist_end":0.03763,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.50068,-0.15517,0.02499],"object_pos_start":[0.50077,-0.15476,0.02493],"object_to_goal_dist_end":0.00522,"object_to_goal_dist_start":0.00482,"object_z_max":0.02541,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2500.0,"raw_peak_contact_force":11.79543,"tcp_end":[0.49117,-0.07045,0.10961],"tcp_start":[0.49454,-0.11797,0.02008],"tcp_to_object_dist_end":0.12012,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```