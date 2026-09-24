## Search State

- **Seed**: 5
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | pose_tolerance | force_exceeded | force_exceeded | 5 | 0.6317 | 0.28 | ✅ accepted |
| 3 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 4 | 0.4640 | 0.18 | ✅ accepted |
| 2 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | pose_tolerance | force_exceeded | time_limit | 4 | 0.3640 | 0.06 | ✅ accepted |
| 1 | push → release → pull → release → release → grasp → retract | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | admittance_control | position_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | time_limit | time_limit | pose_tolerance | 3 | -0.3000 | 0.00 | ❌ rejected |
| 0 | push → release → pull → release → release → grasp → retract | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | admittance_control | position_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | time_limit | time_limit | pose_tolerance | 3 | -0.3000 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.28 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266`
- Frozen object start: [0.5366003508494456, 0.03695289476837925, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5366003508494456, 0.03695289476837925, 0.025)
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
  frozen_object_start: [0.5366, 0.037, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5366003508494456, 0.03695289476837925, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0366, -0.187, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266

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

## Current Skill (Q=0.632) — your mutation base

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
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.1
      axis: task_goal_direction
      mode: add_to_offset
      sign: negative
    tolerance: 0.01
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
- id: contact
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.03
      axis: task_goal_direction
      mode: add_to_offset
      sign: negative
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 1.0
      - 12.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  guards:
  - id: contact_force_guard
    when: during_phase
    predicate: force_below
    threshold: 25.0
    on_failure: abort
- id: push
  type: push
  generator: linear_cartesian
  control: position_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.03
    - 0.0
    offset_along_axis:
      distance: 0.15
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.05
      - 0.35
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_force_limit:
      type: scalar
      range:
      - 10.0
      - 22.0
      default: 18.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: push_force_guard
    when: during_phase
    predicate: force_below
    threshold: 25.0
    on_failure: abort
  subtask_id: push

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.1, mode=add_to_offset, sign=negative}, tolerance=0.01
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **contact** (`contact`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.03, mode=add_to_offset, sign=negative}
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
  - guards:
    - id=contact_force_guard, when=during_phase, predicate=force_below, on_failure=abort, threshold=25.0
- **push** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.03, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.15, mode=add_to_offset, sign=positive}
  - parameter_bindings:
    - push_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_force_limit: status=consumed; consumers=termination.force_threshold (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=push_force_guard, when=during_phase, predicate=force_below, on_failure=abort, threshold=25.0

## Design Metrics

- **Composite score**: 0.632
- **task_score** (E): 0.275
- **fitness_score**: 0.356  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.556
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.2832 |
| contact | 1.00 | 1.00 | 0.0553 |
| push | 1.00 | 1.00 | 0.0536 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.522, 0.110, 0.042) | (0.519, 0.022, 0.025)→(0.519, 0.022, 0.025) | 0.173→0.173 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact | contact | 1.00 / force_exceeded | (0.522, 0.110, 0.042)→(0.517, 0.059, 0.022) | (0.519, 0.022, 0.025)→(0.519, 0.022, 0.025) | 0.173→0.173 | 1.00 / 5.000 | 18.256 | 0.245 |
| push | push | 1.00 / force_exceeded | (0.517, 0.059, 0.022)→(0.506, 0.007, 0.019) | (0.519, 0.022, 0.025)→(0.509, -0.030, 0.025) | 0.173→0.120 | 1.00 / 4.000 | 33.640 | 18.674 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.206
- lateral_force_integral: None
- approach_alignment: 0.422
- goal_progress: 0.204
- terminal_score: 0.204
- phase_score: 0.380
- phase_breakdown.approach_score: 0.645
- phase_breakdown.contact_score: 0.781
- phase_breakdown.push_score: 0.034

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.518
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.621
- **Median Q (composite search score)**: 0.628
- **K-run variance**: 0.0026
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.401


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `7ff7a4e3a1b03e3d7ba3d0b298d1ee8847b5344eb55f2aa0aaf582e7a98ab8ac`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `028a6956ebe09ab7c7952341570355f52da12e46fb22d3462091c70c024324ff`; realized-scene SHA-256: `b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5366,0.03695,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.0366,-0.18695,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5366,0.03695,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.824,"average_solve_count":125.0,"average_success_count":125.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.08586,"contact.contact_force_threshold":8.79267,"push.push_depth":0.22973,"push.push_force_limit":20.19494,"push.push_speed":0.03404},"optimized_scores":{"best_composite_score":0.57121,"best_fitness_score":0.51788,"best_task_score":0.62078},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":854.0,"contact_point_centroid":[0.52956,0.00379,0.03377],"force_p95":12.55865,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.04236,"mean_force":3.65126,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.52281,0.01564,0.01814]},{"body_a":"world","body_b":"push_box","contact_count":1659.0,"contact_point_centroid":[0.5239,-0.02953,-4e-05],"force_p95":6.87273,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.73336,"mean_force":2.27366,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.52321,0.01738,0.01819]},{"body_a":"push_box","body_b":"link7","contact_count":158.0,"contact_point_centroid":[0.54823,-0.00701,0.0502],"force_p95":6.58906,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.83148,"mean_force":1.47402,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.52106,0.00777,0.01796]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.52205,0.06011,0.17214]},{"body_a":"world","body_b":"push_box","contact_count":1916.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.5404,0.09676,0.03286]}],"total_contact_groups":5},"final_pose_error":0.30833,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5142,-0.07917,0.02499],"final_tcp_position":[0.51122,-0.0422,0.01839],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":19.04236,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.54594,0.12016,0.04777],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08677,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":479.0,"n_steps_budget":600.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.02499,"peak_contact_force":16.39623,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1916.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.53844,0.07404,0.02279],"tcp_start":[0.54594,0.12016,0.04777],"tcp_to_object_dist_end":0.0372,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5142,-0.07917,0.02499],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.07224,"object_to_goal_dist_start":0.1905,"object_z_max":0.02531,"peak_contact_force":4.0497,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2671.0,"raw_peak_contact_force":19.04236,"subtask_id":"push","tcp_end":[0.51122,-0.0422,0.01839],"tcp_start":[0.53844,0.07404,0.02279],"tcp_to_object_dist_end":0.03767,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1c6409cc6d884b90ecc3937d36e5ea87cc4ef513b6f301a9da66b4e84390f805`; realized-scene SHA-256: `5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50458,-0.01881,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.00458,-0.13119,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.50458,-0.01881,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.46364,"average_solve_count":110.0,"average_success_count":110.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.06719,"contact.contact_force_threshold":4.29048,"push.push_depth":0.3432,"push.push_force_limit":15.37961,"push.push_speed":0.0271},"optimized_scores":{"best_composite_score":0.6275,"best_fitness_score":0.24084,"best_task_score":0.00066},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.5011,0.00609,0.02084],"force_p95":16.11091,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.11877,"mean_force":8.40503,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50105,0.018,0.0208]},{"body_a":"world","body_b":"push_box","contact_count":8.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":5.29806,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.59516,"mean_force":3.17898,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50106,0.01804,0.02082]},{"body_a":"world","body_b":"push_box","contact_count":3800.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50087,0.03817,0.16538]},{"body_a":"world","body_b":"push_box","contact_count":2080.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.50055,0.04786,0.02468]}],"total_contact_groups":4},"final_pose_error":0.481,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50454,-0.01889,0.02499],"final_tcp_position":[0.50097,0.01782,0.0207],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":29.10514,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":950.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3800.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.50362,0.0768,0.03255],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.09591,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":520.0,"n_steps_budget":600.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":26.14208,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2080.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.50107,0.01809,0.02084],"tcp_start":[0.50362,0.0768,0.03255],"tcp_to_object_dist_end":0.03729,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50454,-0.01889,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13119,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":29.10514,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":11.0,"raw_peak_contact_force":17.11877,"subtask_id":"push","tcp_end":[0.50097,0.01782,0.0207],"tcp_start":[0.50107,0.01809,0.02084],"tcp_to_object_dist_end":0.03713,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f52ec1899e2888770a8b6b3ae605718303ef4b10e72cfd7d20ce53303721b2b0`; realized-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51501,0.04767,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.01501,-0.19767,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.51501,0.04767,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.79439,"average_solve_count":107.0,"average_success_count":107.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.07946,"contact.contact_force_threshold":2.68372,"push.push_depth":0.33254,"push.push_force_limit":18.03323,"push.push_speed":0.02489},"optimized_scores":{"best_composite_score":0.69651,"best_fitness_score":0.30984,"best_task_score":0.20448},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":230.0,"contact_point_centroid":[0.51363,0.05299,0.03078],"force_p95":14.97618,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.86172,"mean_force":5.39776,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50801,0.06484,0.01886]},{"body_a":"world","body_b":"push_box","contact_count":498.0,"contact_point_centroid":[0.51006,0.0234,-6e-05],"force_p95":9.2768,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.9786,"mean_force":3.31919,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50814,0.06594,0.01892]},{"body_a":"push_box","body_b":"link7","contact_count":80.0,"contact_point_centroid":[0.53534,0.05078,0.0501],"force_p95":14.09408,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.78618,"mean_force":5.62067,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50756,0.06372,0.01842]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50726,0.06599,0.1716]},{"body_a":"world","body_b":"push_box","contact_count":1944.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.51292,0.10805,0.03239]}],"total_contact_groups":5},"final_pose_error":0.49707,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50737,0.00753,0.02488],"final_tcp_position":[0.5058,0.04447,0.01809],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":67.76619,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.51645,0.13208,0.04639],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0871,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":486.0,"n_steps_budget":600.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":12.23032,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1944.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.51281,0.08464,0.02277],"tcp_start":[0.51645,0.13208,0.04639],"tcp_to_object_dist_end":0.03711,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":279.0,"n_steps_budget":1000.0,"object_pos_end":[0.50737,0.00753,0.02488],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.1577,"object_to_goal_dist_start":0.19823,"object_z_max":0.02544,"peak_contact_force":67.76619,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":808.0,"raw_peak_contact_force":19.86172,"subtask_id":"push","tcp_end":[0.5058,0.04447,0.01809],"tcp_start":[0.51281,0.08464,0.02277],"tcp_to_object_dist_end":0.03759,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```