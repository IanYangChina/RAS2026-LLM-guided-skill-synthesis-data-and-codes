## Search State

- **Seed**: 0
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 2 | 0.8721 | 0.82 | ❌ rejected |
| 8 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 2 | 0.7604 | 0.71 | ❌ rejected |
| 7 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 2 | 0.8808 | 0.84 | ❌ rejected |
| 6 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 2 | 0.8758 | 0.83 | ❌ rejected |
| 5 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 2 | 0.8771 | 0.84 | ❌ rejected |

**Proposal policy**: task_score is 0.82 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.872) — your mutation base

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

- **Composite score**: 0.872
- **task_score** (E): 0.823
- **fitness_score**: 0.782  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.160

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2812 |
| contact_1 | 1.00 | 1.00 | 0.0405 |
| push_1 | 1.00 | 1.00 | 0.1472 |
| retract_1 | 1.00 | 1.00 | 0.1014 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.493, 0.077, 0.033) | (0.496, 0.001, 0.025)→(0.496, 0.001, 0.025) | 0.152→0.152 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / force_exceeded | (0.493, 0.077, 0.033)→(0.492, 0.038, 0.022) | (0.496, 0.001, 0.025)→(0.496, 0.001, 0.025) | 0.152→0.152 | 1.00 / 5.000 | 27.512 | 0.245 |
| push_1 | push | 1.00 / step_budget | (0.492, 0.038, 0.022)→(0.497, -0.108, 0.021) | (0.496, 0.001, 0.025)→(0.523, -0.137, 0.028) | 0.152→0.031 | 1.00 / 3.667 | 25.746 | 47.249 |
| retract_1 | retract | 1.00 / step_budget | (0.497, -0.108, 0.021)→(0.494, -0.061, 0.111) | (0.523, -0.137, 0.028)→(0.521, -0.137, 0.025) | 0.031→0.029 | 1.00 / 4.000 | 0.245 | 26.084 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.672
- goal_progress: 0.926
- terminal_score: 0.926
- phase_score: 0.822
- phase_breakdown.push_score: 0.853
- phase_breakdown.contact_score: 0.771
- phase_breakdown.approach_score: 0.819

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.863
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.926
- **Median Q (composite search score)**: 0.906
- **K-run variance**: 0.0070
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 11.0
- **Final σ (mean)**: 0.551


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.76923,"average_solve_count":130.0,"average_success_count":130.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":16.89683,"push_1.push_depth":0.02105},"optimized_scores":{"best_composite_score":0.90595,"best_fitness_score":0.81595,"best_task_score":0.79917},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":423.0,"contact_point_centroid":[0.53407,-0.09272,0.05409],"force_p95":34.88361,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.48622,"mean_force":20.32717,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50087,-0.08323,0.02012]},{"body_a":"attachment","body_b":"push_box","contact_count":646.0,"contact_point_centroid":[0.51433,-0.07089,0.04693],"force_p95":28.44551,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.90822,"mean_force":11.71619,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50257,-0.06139,0.01947]},{"body_a":"world","body_b":"push_box","contact_count":1035.0,"contact_point_centroid":[0.53302,-0.11204,-8e-05],"force_p95":28.64092,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":34.85307,"mean_force":13.82803,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50255,-0.06307,0.01964]},{"body_a":"push_box","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.53615,-0.12419,0.05487],"force_p95":31.57773,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.49518,"mean_force":12.20095,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49853,-0.11888,0.02183]},{"body_a":"world","body_b":"push_box","contact_count":2330.0,"contact_point_centroid":[0.52585,-0.14727,-1e-05],"force_p95":0.39122,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.57912,"mean_force":0.28921,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4952,-0.0924,0.06888]},{"body_a":"attachment","body_b":"push_box","contact_count":47.0,"contact_point_centroid":[0.51436,-0.11988,0.05493],"force_p95":12.25754,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.86962,"mean_force":1.81752,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49673,-0.11518,0.02642]},{"body_a":"world","body_b":"push_box","contact_count":3496.0,"contact_point_centroid":[0.51644,-0.02763,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50494,0.02455,0.16585]},{"body_a":"world","body_b":"push_box","contact_count":1896.0,"contact_point_centroid":[0.51644,-0.02763,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50996,0.02902,0.02519]}],"total_contact_groups":8},"final_pose_error":0.01136,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52456,-0.14661,0.02499],"final_tcp_position":[0.49539,-0.07127,0.11119],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51644,-0.02763,0.025]},"peak_contact_force":48.48622,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":874.0,"n_steps_budget":1000.0,"object_pos_end":[0.51644,-0.02763,0.02499],"object_pos_start":[0.51644,-0.02763,0.025],"object_to_goal_dist_end":0.12347,"object_to_goal_dist_start":0.12347,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3496.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.51171,0.04945,0.03319],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07766,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":474.0,"n_steps_budget":600.0,"object_pos_end":[0.51644,-0.02763,0.02499],"object_pos_start":[0.51644,-0.02763,0.02499],"object_to_goal_dist_end":0.12347,"object_to_goal_dist_start":0.12347,"object_z_max":0.02499,"peak_contact_force":26.84816,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1896.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.51153,0.00931,0.02129],"tcp_start":[0.51171,0.04945,0.03319],"tcp_to_object_dist_end":0.03745,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":736.0,"n_steps_budget":870.0,"object_pos_end":[0.52783,-0.14754,0.02926],"object_pos_start":[0.51644,-0.02763,0.02499],"object_to_goal_dist_end":0.02826,"object_to_goal_dist_start":0.12347,"object_z_max":0.02936,"peak_contact_force":33.91224,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2104.0,"raw_peak_contact_force":48.48622,"subtask_id":"push","tcp_end":[0.49878,-0.1188,0.02175],"tcp_start":[0.51153,0.00931,0.02129],"tcp_to_object_dist_end":0.04155,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.52456,-0.14661,0.02499],"object_pos_start":[0.52783,-0.14754,0.02926],"object_to_goal_dist_end":0.0248,"object_to_goal_dist_start":0.02826,"object_z_max":0.02932,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2384.0,"raw_peak_contact_force":34.49518,"tcp_end":[0.49539,-0.07127,0.11119],"tcp_start":[0.49878,-0.1188,0.02175],"tcp_to_object_dist_end":0.11814,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.7931,"average_solve_count":145.0,"average_success_count":145.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":13.02846,"push_1.push_depth":0.04936},"optimized_scores":{"best_composite_score":0.75674,"best_fitness_score":0.66674,"best_task_score":0.74337},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":681.0,"contact_point_centroid":[0.53055,-0.03443,0.05427],"force_p95":42.64166,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":55.18041,"mean_force":24.73425,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49624,-0.02701,0.02042]},{"body_a":"world","body_b":"push_box","contact_count":1502.0,"contact_point_centroid":[0.53209,-0.05509,-7e-05],"force_p95":33.82941,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":41.83776,"mean_force":17.19474,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49593,-0.01071,0.02012]},{"body_a":"attachment","body_b":"push_box","contact_count":880.0,"contact_point_centroid":[0.5091,-0.01416,0.04814],"force_p95":31.919,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.41723,"mean_force":15.53604,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49575,-0.00625,0.01995]},{"body_a":"push_box","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.53497,-0.08254,0.0553],"force_p95":29.60647,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.64704,"mean_force":10.64695,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49771,-0.08465,0.02212]},{"body_a":"world","body_b":"push_box","contact_count":2250.0,"contact_point_centroid":[0.53173,-0.10747,-2e-05],"force_p95":0.55478,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.74731,"mean_force":0.29641,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49442,-0.05776,0.07043]},{"body_a":"attachment","body_b":"push_box","contact_count":67.0,"contact_point_centroid":[0.5135,-0.0818,0.05534],"force_p95":7.14908,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.48175,"mean_force":1.4083,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49558,-0.0796,0.02898]},{"body_a":"world","body_b":"push_box","contact_count":3980.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49785,0.06389,0.16385]},{"body_a":"world","body_b":"push_box","contact_count":1828.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49549,0.10863,0.02431]}],"total_contact_groups":8},"final_pose_error":0.01133,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5299,-0.10701,0.02499],"final_tcp_position":[0.49463,-0.03723,0.11153],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":55.18041,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":995.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3980.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.49751,0.12763,0.03133],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07395,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":457.0,"n_steps_budget":600.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.02499,"peak_contact_force":29.49103,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1828.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.49665,0.09103,0.02131],"tcp_start":[0.49751,0.12763,0.03133],"tcp_to_object_dist_end":0.03746,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53392,-0.10737,0.02949],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.05467,"object_to_goal_dist_start":0.20406,"object_z_max":0.02959,"peak_contact_force":34.90697,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3063.0,"raw_peak_contact_force":55.18041,"subtask_id":"push","tcp_end":[0.49801,-0.08454,0.022],"tcp_start":[0.49665,0.09103,0.02131],"tcp_to_object_dist_end":0.04321,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.5299,-0.10701,0.02499],"object_pos_start":[0.53392,-0.10737,0.02949],"object_to_goal_dist_end":0.05237,"object_to_goal_dist_start":0.05467,"object_z_max":0.02989,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2325.0,"raw_peak_contact_force":35.64704,"tcp_end":[0.49463,-0.03723,0.11153],"tcp_start":[0.49801,-0.08454,0.022],"tcp_to_object_dist_end":0.11663,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.77273,"average_solve_count":132.0,"average_success_count":132.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":10.73515,"push_1.push_depth":0.02082},"optimized_scores":{"best_composite_score":0.95346,"best_fitness_score":0.86346,"best_task_score":0.9257},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":693.0,"contact_point_centroid":[0.48475,-0.06768,0.03714],"force_p95":21.81096,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.07965,"mean_force":5.63078,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47978,-0.05585,0.01961]},{"body_a":"world","body_b":"push_box","contact_count":1050.0,"contact_point_centroid":[0.48948,-0.10765,-6e-05],"force_p95":11.67252,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.11395,"mean_force":4.13851,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47895,-0.05206,0.01961]},{"body_a":"attachment","body_b":"push_box","contact_count":7.0,"contact_point_centroid":[0.50227,-0.13234,0.04925],"force_p95":6.14195,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.11083,"mean_force":1.59312,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49373,-0.12054,0.02154]},{"body_a":"world","body_b":"push_box","contact_count":2481.0,"contact_point_centroid":[0.50717,-0.15679,-2e-05],"force_p95":0.24666,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.83685,"mean_force":0.25531,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4912,-0.09656,0.06484]},{"body_a":"world","body_b":"push_box","contact_count":3432.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48376,0.02618,0.16621]},{"body_a":"world","body_b":"push_box","contact_count":1884.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46666,0.03231,0.02648]}],"total_contact_groups":6},"final_pose_error":0.01129,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50705,-0.1565,0.02499],"final_tcp_position":[0.49132,-0.07411,0.10966],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":38.07965,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":858.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3432.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.46921,0.05269,0.0342],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07745,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":471.0,"n_steps_budget":600.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":26.19751,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1884.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.4672,0.0128,0.02227],"tcp_start":[0.46921,0.05269,0.0342],"tcp_to_object_dist_end":0.03731,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":818.0,"n_steps_budget":930.0,"object_pos_end":[0.50749,-0.15711,0.02586],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.01036,"object_to_goal_dist_start":0.12903,"object_z_max":0.02639,"peak_contact_force":8.42028,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1743.0,"raw_peak_contact_force":38.07965,"subtask_id":"push","tcp_end":[0.4947,-0.12165,0.02015],"tcp_start":[0.4672,0.0128,0.02227],"tcp_to_object_dist_end":0.03812,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.50705,-0.1565,0.02499],"object_pos_start":[0.50749,-0.15711,0.02586],"object_to_goal_dist_end":0.00959,"object_to_goal_dist_start":0.01036,"object_z_max":0.02606,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2488.0,"raw_peak_contact_force":8.11083,"tcp_end":[0.49132,-0.07411,0.10966],"tcp_start":[0.4947,-0.12165,0.02015],"tcp_to_object_dist_end":0.11918,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```