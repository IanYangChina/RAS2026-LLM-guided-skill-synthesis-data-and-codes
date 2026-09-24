## Search State

- **Seed**: 2
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 5 | 0.3058 | 0.06 | ❌ rejected |
| 2 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 4 | 0.4941 | 0.01 | ❌ rejected |
| 1 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.3569 | 0.12 | ❌ rejected |
| 0 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 2 | 0.6527 | 0.88 | ✅ accepted |

**Proposal policy**: task_score is 0.06 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `8c36a5f9300ba3a57ccc09620ec8ba0a5276276ed83fb4303679e150911bfa14`
- Frozen object start: [0.47139345610991795, -0.0241810627903052, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.47139345610991795, -0.0241810627903052, 0.025)
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
  frozen_object_start: [0.4714, -0.0242, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.47139345610991795, -0.0241810627903052, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [0.0286, -0.1258, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 8c36a5f9300ba3a57ccc09620ec8ba0a5276276ed83fb4303679e150911bfa14

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

## Current Skill (Q=0.306) — your mutation base

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
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
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
    orientation:
      mode: keep_current
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
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
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.08, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.03, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **push_1** (`push`)
  - target: source=yaml, anchor=task_goal, entity=goal_marker, offset=[0.0, 0.03, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.3]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.306
- **task_score** (E): 0.060
- **fitness_score**: 0.199  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.417
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2377 |
| contact_1 | 0.67 | 1.00 | 0.0945 |
| push_1 | 1.00 | 1.00 | 0.0018 |
| retract_1 | 0.00 | 1.00 | 0.1644 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.476, 0.080, 0.092) | (0.492, -0.018, 0.025)→(0.492, -0.018, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 0.67 / force_exceeded | (0.476, 0.080, 0.092)→(0.486, 0.012, 0.031) | (0.492, -0.018, 0.025)→(0.493, -0.024, 0.025) | 0.139→0.133 | 1.00 / 3.000 | 17.987 | 20.099 |
| push_1 | push | 1.00 / force_exceeded | (0.486, 0.012, 0.031)→(0.485, 0.011, 0.030) | (0.493, -0.024, 0.025)→(0.493, -0.025, 0.025) | 0.133→0.132 | 1.00 / 3.333 | 18.908 | 9.202 |
| retract_1 | retract | 0.00 / step_budget | (0.485, 0.011, 0.030)→(0.483, 0.011, 0.195) | (0.493, -0.025, 0.025)→(0.492, -0.026, 0.025) | 0.132→0.131 | 1.00 / 4.000 | 0.245 | 10.172 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.055
- lateral_force_integral: None
- approach_alignment: 0.439
- goal_progress: 0.052
- terminal_score: 0.052
- phase_score: 0.307
- phase_breakdown.contact_score: 0.752
- phase_breakdown.push_score: 0.067
- phase_breakdown.approach_score: 0.239

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.218
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.108
- **Median Q (composite search score)**: 0.365
- **K-run variance**: 0.0111
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.374


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `27920116be2b9a598fe307ae470bb0295293d051bb1ef513a0996a4d851f2459`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `1a1e2536715050e6c37d8aed13e4ecd62004f6234f1413b07d7b475a233f55c9`; realized-scene SHA-256: `8c36a5f9300ba3a57ccc09620ec8ba0a5276276ed83fb4303679e150911bfa14`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47139,-0.02418,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02861,-0.12582,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47139,-0.02418,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89516,"average_solve_count":124.0,"average_success_count":124.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_offset":0.08315,"approach_1.approach_speed":0.07145,"contact_1.contact_force_threshold":21.69364,"push_1.push_distance":0.28722,"push_1.push_speed":0.08344},"optimized_scores":{"best_composite_score":0.39477,"best_fitness_score":0.20477,"best_task_score":0.05212},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":54.0,"contact_point_centroid":[0.46271,-0.00253,0.04796],"force_p95":20.06305,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.56462,"mean_force":14.37076,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46003,0.00938,0.03773]},{"body_a":"world","body_b":"push_box","contact_count":1827.0,"contact_point_centroid":[0.47151,-0.02503,-1e-05],"force_p95":2.75807,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.67659,"mean_force":0.67345,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.45504,0.03061,0.06387]},{"body_a":"attachment","body_b":"push_box","contact_count":71.0,"contact_point_centroid":[0.46163,-0.00766,0.0502],"force_p95":1.44203,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.8442,"mean_force":0.75693,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.45829,0.00422,0.04077]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.46353,-0.00665,0.04122],"force_p95":8.43871,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.77297,"mean_force":5.4304,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46086,0.00529,0.03285]},{"body_a":"world","body_b":"push_box","contact_count":19.0,"contact_point_centroid":[0.475,-0.05562,-5e-05],"force_p95":2.59915,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.56057,"mean_force":1.11559,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46082,0.00529,0.03277]},{"body_a":"world","body_b":"push_box","contact_count":3757.0,"contact_point_centroid":[0.47074,-0.03279,-1e-05],"force_p95":0.35962,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.18114,"mean_force":0.26035,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.45751,0.00433,0.11915]},{"body_a":"world","body_b":"push_box","contact_count":2800.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47582,0.02616,0.1968]}],"total_contact_groups":7},"final_pose_error":0.13472,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.4706,-0.03128,0.02499],"final_tcp_position":[0.45783,0.00436,0.19756],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":32.56462,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":700.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2800.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.4526,0.05307,0.09411],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10535,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":482.0,"n_steps_budget":600.0,"object_pos_end":[0.47184,-0.03029,0.02509],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12297,"object_to_goal_dist_start":0.12903,"object_z_max":0.02517,"peak_contact_force":32.56462,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1881.0,"raw_peak_contact_force":32.56462,"subtask_id":"contact","tcp_end":[0.46112,0.00605,0.03339],"tcp_start":[0.4526,0.05307,0.09411],"tcp_to_object_dist_end":0.03879,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":15.0,"n_steps_budget":1000.0,"object_pos_end":[0.47198,-0.03161,0.02519],"object_pos_start":[0.47184,-0.03029,0.02509],"object_to_goal_dist_end":0.12167,"object_to_goal_dist_start":0.12297,"object_z_max":0.02556,"peak_contact_force":26.21635,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":21.0,"raw_peak_contact_force":8.77297,"subtask_id":"push","tcp_end":[0.46056,0.00441,0.03225],"tcp_start":[0.46112,0.00605,0.03339],"tcp_to_object_dist_end":0.03843,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4706,-0.03128,0.02499],"object_pos_start":[0.47198,-0.03161,0.02519],"object_to_goal_dist_end":0.12231,"object_to_goal_dist_start":0.12167,"object_z_max":0.02553,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3828.0,"raw_peak_contact_force":9.8442,"tcp_end":[0.45783,0.00436,0.19756],"tcp_start":[0.46056,0.00441,0.03225],"tcp_to_object_dist_end":0.17667,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `e864853e179d3df1b19d9aaa17e18a5fe8c66fe7533fc0dd3a88a693de7416e7`; realized-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45028,-0.03158,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.04972,-0.11842,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.45028,-0.03158,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.30159,"average_solve_count":189.0,"average_success_count":189.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_offset":0.14601,"approach_1.approach_speed":0.04242,"contact_1.contact_force_threshold":20.84418,"push_1.push_distance":0.23697,"push_1.push_speed":0.03999},"optimized_scores":{"best_composite_score":0.15814,"best_fitness_score":0.21814,"best_task_score":0.10794},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":66.0,"contact_point_centroid":[0.43822,-0.0123,0.04773],"force_p95":17.10535,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.48859,"mean_force":7.03964,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.43389,-0.00041,0.02924]},{"body_a":"world","body_b":"push_box","contact_count":3029.0,"contact_point_centroid":[0.45061,-0.03252,-1e-05],"force_p95":0.28619,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.26347,"mean_force":0.40603,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.41361,0.04846,0.05988]},{"body_a":"world","body_b":"push_box","contact_count":6.0,"contact_point_centroid":[0.48032,-0.05073,-9e-05],"force_p95":0.87946,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.89776,"mean_force":0.64049,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.43684,-0.0077,0.02466]},{"body_a":"world","body_b":"push_box","contact_count":3999.0,"contact_point_centroid":[0.45499,-0.04465,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.83253,"mean_force":0.24571,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.43387,-0.00786,0.1071]},{"body_a":"world","body_b":"push_box","contact_count":3528.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44736,0.04841,0.19504]}],"total_contact_groups":5},"final_pose_error":0.13432,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.45498,-0.04464,0.02499],"final_tcp_position":[0.43408,-0.00784,0.19022],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":27.48859,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":882.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3528.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.39629,0.09722,0.09271],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.15522,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":812.0,"n_steps_budget":870.0,"object_pos_end":[0.45502,-0.04383,0.02509],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.11531,"object_to_goal_dist_start":0.12843,"object_z_max":0.02526,"peak_contact_force":0.98259,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3095.0,"raw_peak_contact_force":27.48859,"subtask_id":"contact","tcp_end":[0.43688,-0.00755,0.02477],"tcp_start":[0.39629,0.09722,0.09271],"tcp_to_object_dist_end":0.04056,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.455,-0.04425,0.02493],"object_pos_start":[0.45502,-0.04383,0.02509],"object_to_goal_dist_end":0.11493,"object_to_goal_dist_start":0.11531,"object_z_max":0.02509,"peak_contact_force":14.50825,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":0.89776,"subtask_id":"push","tcp_end":[0.43678,-0.00787,0.02451],"tcp_start":[0.43688,-0.00755,0.02477],"tcp_to_object_dist_end":0.04069,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45498,-0.04464,0.02499],"object_pos_start":[0.455,-0.04425,0.02493],"object_to_goal_dist_end":0.11457,"object_to_goal_dist_start":0.11493,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3999.0,"raw_peak_contact_force":0.83253,"tcp_end":[0.43408,-0.00784,0.19022],"tcp_start":[0.43678,-0.00787,0.02451],"tcp_to_object_dist_end":0.17057,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `c820cf29ab3e34ea9695cb40d5aba5de55f3ad951ee91f0df578ae7146ee7727`; realized-scene SHA-256: `721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.55317,0.00136,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.05317,-0.15136,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.55317,0.00136,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.72093,"average_solve_count":129.0,"average_success_count":129.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_offset":0.09809,"approach_1.approach_speed":0.06961,"contact_1.contact_force_threshold":17.29854,"push_1.push_distance":0.27863,"push_1.push_speed":0.03512},"optimized_scores":{"best_composite_score":0.36456,"best_fitness_score":0.17456,"best_task_score":0.02111},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":7.0,"contact_point_centroid":[0.55938,0.02444,0.04094],"force_p95":15.65773,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.84018,"mean_force":4.31505,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.55779,0.0364,0.03479]},{"body_a":"attachment","body_b":"push_box","contact_count":7.0,"contact_point_centroid":[0.56003,0.02609,0.03584],"force_p95":13.61973,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.93385,"mean_force":4.50069,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.56001,0.03805,0.03582]},{"body_a":"world","body_b":"push_box","contact_count":3965.0,"contact_point_centroid":[0.55089,-0.00147,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.77926,"mean_force":0.25378,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.55511,0.03634,0.11417]},{"body_a":"world","body_b":"push_box","contact_count":34.0,"contact_point_centroid":[0.55556,-0.00246,-4e-05],"force_p95":4.10831,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.40537,"mean_force":1.19696,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.55943,0.03749,0.0353]},{"body_a":"world","body_b":"push_box","contact_count":3668.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.53805,0.04446,0.19263]},{"body_a":"world","body_b":"push_box","contact_count":1748.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.56755,0.06345,0.05986]}],"total_contact_groups":6},"final_pose_error":0.13801,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.55084,-0.00142,0.02499],"final_tcp_position":[0.55574,0.03641,0.1966],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":20.41399,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":917.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3668.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.57792,0.08894,0.08857],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11102,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":437.0,"n_steps_budget":630.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":20.41399,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1748.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.56028,0.03829,0.0361],"tcp_start":[0.57792,0.08894,0.08857],"tcp_to_object_dist_end":0.03922,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":15.0,"n_steps_budget":1000.0,"object_pos_end":[0.55229,-0.00032,0.02488],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.15855,"object_to_goal_dist_start":0.16043,"object_z_max":0.02503,"peak_contact_force":16.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":41.0,"raw_peak_contact_force":17.93385,"subtask_id":"push","tcp_end":[0.55863,0.03666,0.03459],"tcp_start":[0.56028,0.03829,0.0361],"tcp_to_object_dist_end":0.03875,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55084,-0.00142,0.02499],"object_pos_start":[0.55229,-0.00032,0.02488],"object_to_goal_dist_end":0.15704,"object_to_goal_dist_start":0.15855,"object_z_max":0.02522,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3972.0,"raw_peak_contact_force":19.84018,"tcp_end":[0.55574,0.03641,0.1966],"tcp_start":[0.55863,0.03666,0.03459],"tcp_to_object_dist_end":0.1758,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```