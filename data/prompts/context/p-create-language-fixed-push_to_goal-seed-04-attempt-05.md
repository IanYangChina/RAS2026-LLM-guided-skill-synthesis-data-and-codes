## Search State

- **Seed**: 4
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.6406 | 0.70 | ✅ accepted |
| 4 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.4187 | 0.66 | ❌ rejected |
| 3 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.6216 | 0.64 | ❌ rejected |
| 2 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.6395 | 0.68 | ✅ accepted |
| 1 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 1 | 0.7753 | 0.44 | ❌ rejected |

**Proposal policy**: task_score is 0.70 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702`
- Frozen object start: [0.5531667326686841, 0.0013593063377233885, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5531667326686841, 0.0013593063377233885, 0.025)
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
  frozen_object_start: [0.5532, 0.0014, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5531667326686841, 0.0013593063377233885, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0532, -0.1514, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702

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

## Current Skill (Q=0.641) — your mutation base

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
      - 0.5
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    approach_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
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
    - -0.01
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
      default: 10
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
    anchor: task_object
    entity: push_box
    offset:
    - 0.0
    - -0.01
    - 0.0
    offset_along_axis:
      distance: 0.25
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.25
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_tolerance:
      type: scalar
      range:
      - 0.005
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
    orientation:
      mode: keep_current
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.01
      - 0.5
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.08, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, -0.01, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, -0.01, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.25, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.3]
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.641
- **task_score** (E): 0.698
- **fitness_score**: 0.751  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2735 |
| contact_1 | 1.00 | 1.00 | 0.0380 |
| push_1 | 1.00 | 1.00 | 0.1762 |
| retract_1 | 1.00 | 1.00 | 0.2754 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.526, 0.079, 0.042) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / force_exceeded | (0.526, 0.079, 0.042)→(0.524, 0.043, 0.029) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 | 1.00 / 5.000 | 39.044 | 0.245 |
| push_1 | push | 1.00 / step_budget | (0.524, 0.043, 0.029)→(0.500, -0.130, 0.021) | (0.531, 0.007, 0.025)→(0.544, -0.132, 0.026) | 0.161→0.050 | 1.00 / 3.333 | 20.651 | 84.412 |
| retract_1 | retract | 1.00 / step_budget | (0.500, -0.130, 0.021)→(0.499, -0.130, 0.297) | (0.544, -0.132, 0.026)→(0.544, -0.132, 0.025) | 0.050→0.049 | 1.00 / 4.000 | 0.245 | 0.975 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 1.000
- goal_progress: 0.790
- terminal_score: 0.790
- phase_score: 0.816
- phase_breakdown.contact_score: 0.748
- phase_breakdown.push_score: 0.912
- phase_breakdown.approach_score: 0.675

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.805
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.790
- **Median Q (composite search score)**: 0.672
- **K-run variance**: 0.0038
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.314


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `8d5a7e825d9524a0954b44a69bda19e1d764760f64bb1262d03aec3c389fadbb`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `c4094dd933e0897d422d7ea261a82b80810f7dec183b19c1da5b940157e7d0c4`; realized-scene SHA-256: `721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.55317,0.00136,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.05317,-0.15136,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.55317,0.00136,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.48544,"average_solve_count":103.0,"average_success_count":103.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.24122,"approach_1.approach_tolerance":0.02366,"contact_1.contact_force":12.55284,"push_1.push_distance":0.17753,"push_1.push_tolerance":0.03755,"retract_1.retract_speed":0.33618},"optimized_scores":{"best_composite_score":0.55421,"best_fitness_score":0.66421,"best_task_score":0.59239},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":107.0,"contact_point_centroid":[0.53654,-0.0307,0.04185],"force_p95":21.57132,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":60.56947,"mean_force":4.50127,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52834,-0.02059,0.02584]},{"body_a":"world","body_b":"push_box","contact_count":374.0,"contact_point_centroid":[0.55715,-0.09253,-0.00019],"force_p95":9.6119,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.24747,"mean_force":1.89296,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51379,-0.08119,0.02322]},{"body_a":"push_box","body_b":"link7","contact_count":10.0,"contact_point_centroid":[0.56005,-0.03931,0.05687],"force_p95":18.47498,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.03131,"mean_force":7.15099,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52255,-0.04318,0.02408]},{"body_a":"world","body_b":"push_box","contact_count":2284.0,"contact_point_centroid":[0.55276,-0.11137,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24579,"mean_force":0.24521,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49744,-0.13922,0.14844]},{"body_a":"world","body_b":"push_box","contact_count":1668.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52164,0.03582,0.17382]},{"body_a":"world","body_b":"push_box","contact_count":1004.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54288,0.05624,0.03615]}],"total_contact_groups":6},"final_pose_error":0.02463,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.55276,-0.11137,0.02499],"final_tcp_position":[0.49871,-0.13921,0.29635],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":60.56947,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":417.0,"n_steps_budget":780.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1668.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.54497,0.07316,0.0453],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07506,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":251.0,"n_steps_budget":600.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":39.57743,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1004.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.54415,0.03833,0.03114],"tcp_start":[0.54497,0.07316,0.0453],"tcp_to_object_dist_end":0.03855,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":240.0,"n_steps_budget":1000.0,"object_pos_end":[0.55273,-0.11138,0.02494],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.06536,"object_to_goal_dist_start":0.16043,"object_z_max":0.02879,"peak_contact_force":0.24588,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":491.0,"raw_peak_contact_force":60.56947,"subtask_id":"push","tcp_end":[0.4999,-0.13953,0.02094],"tcp_start":[0.54415,0.03833,0.03114],"tcp_to_object_dist_end":0.05999,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":571.0,"n_steps_budget":600.0,"object_pos_end":[0.55276,-0.11137,0.02499],"object_pos_start":[0.55273,-0.11138,0.02494],"object_to_goal_dist_end":0.06539,"object_to_goal_dist_start":0.06536,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2284.0,"raw_peak_contact_force":0.24579,"tcp_end":[0.49871,-0.13921,0.29635],"tcp_start":[0.4999,-0.13953,0.02094],"tcp_to_object_dist_end":0.27809,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `452b4d03bf1b69f7d6475210c4cc0fbd85197208ecbf5594cd2cfcf54c82bcbb`; realized-scene SHA-256: `b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5366,0.03695,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.0366,-0.18695,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5366,0.03695,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.4466,"average_solve_count":103.0,"average_success_count":103.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.29664,"approach_1.approach_tolerance":0.01357,"contact_1.contact_force":3.45083,"push_1.push_distance":0.19793,"push_1.push_tolerance":0.04368,"retract_1.retract_speed":0.42145},"optimized_scores":{"best_composite_score":0.67222,"best_fitness_score":0.78222,"best_task_score":0.71078},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":215.0,"contact_point_centroid":[0.55245,-0.07089,-0.0002],"force_p95":67.94525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":107.03493,"mean_force":15.07661,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51357,-0.03673,0.02213]},{"body_a":"push_box","body_b":"link7","contact_count":53.0,"contact_point_centroid":[0.54774,-0.06539,0.05421],"force_p95":80.08635,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":99.77001,"mean_force":38.341,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51027,-0.06084,0.0213]},{"body_a":"attachment","body_b":"push_box","contact_count":129.0,"contact_point_centroid":[0.52573,-0.02198,0.0408],"force_p95":40.71065,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":88.03601,"mean_force":10.05304,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51645,-0.01349,0.02229]},{"body_a":"world","body_b":"push_box","contact_count":2261.0,"contact_point_centroid":[0.55123,-0.13055,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49271,"mean_force":0.24768,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49975,-0.1243,0.14969]},{"body_a":"world","body_b":"push_box","contact_count":2420.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51444,0.05365,0.16858]},{"body_a":"world","body_b":"push_box","contact_count":1004.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52842,0.09193,0.02934]}],"total_contact_groups":6},"final_pose_error":0.02461,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.55144,-0.13026,0.02499],"final_tcp_position":[0.50103,-0.12423,0.29632],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":107.03493,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":605.0,"n_steps_budget":660.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2420.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.53088,0.10916,0.0362],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0733,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":251.0,"n_steps_budget":600.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.02499,"peak_contact_force":43.52535,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1004.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.52907,0.07389,0.02611],"tcp_start":[0.53088,0.10916,0.0362],"tcp_to_object_dist_end":0.03772,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":233.0,"n_steps_budget":1000.0,"object_pos_end":[0.55078,-0.13051,0.02448],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.05439,"object_to_goal_dist_start":0.1905,"object_z_max":0.02984,"peak_contact_force":0.47615,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":397.0,"raw_peak_contact_force":107.03493,"subtask_id":"push","tcp_end":[0.50224,-0.1245,0.02089],"tcp_start":[0.52907,0.07389,0.02611],"tcp_to_object_dist_end":0.04904,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":571.0,"n_steps_budget":600.0,"object_pos_end":[0.55144,-0.13026,0.02499],"object_pos_start":[0.55078,-0.13051,0.02448],"object_to_goal_dist_end":0.0551,"object_to_goal_dist_start":0.05439,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2261.0,"raw_peak_contact_force":0.49271,"tcp_end":[0.50103,-0.12423,0.29632],"tcp_start":[0.50224,-0.1245,0.02089],"tcp_to_object_dist_end":0.27603,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e3aaa9b30183e782395a479a1824f41a69a2557638e862a63e7a5368dd2a464a`; realized-scene SHA-256: `5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50458,-0.01881,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.00458,-0.13119,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.50458,-0.01881,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.49438,"average_solve_count":89.0,"average_success_count":89.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.33665,"approach_1.approach_tolerance":0.02009,"contact_1.contact_force":10.64933,"push_1.push_distance":0.13733,"push_1.push_tolerance":0.04022,"retract_1.retract_speed":0.35196},"optimized_scores":{"best_composite_score":0.69547,"best_fitness_score":0.80547,"best_task_score":0.79007},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":110.0,"contact_point_centroid":[0.50561,-0.06474,0.04204],"force_p95":24.16245,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":85.63188,"mean_force":6.44055,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49729,-0.05441,0.02493]},{"body_a":"world","body_b":"push_box","contact_count":131.0,"contact_point_centroid":[0.52627,-0.09221,-8e-05],"force_p95":30.05411,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":63.54766,"mean_force":8.25556,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49744,-0.04693,0.02556]},{"body_a":"push_box","body_b":"link7","contact_count":12.0,"contact_point_centroid":[0.53506,-0.11305,0.05466],"force_p95":58.99354,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":61.23143,"mean_force":23.03076,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49715,-0.11235,0.02195]},{"body_a":"world","body_b":"push_box","contact_count":2144.0,"contact_point_centroid":[0.52831,-0.15592,-1e-05],"force_p95":0.34693,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.18505,"mean_force":0.26376,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49492,-0.1261,0.15707]},{"body_a":"attachment","body_b":"push_box","contact_count":29.0,"contact_point_centroid":[0.51292,-0.13132,0.05391],"force_p95":1.35968,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.5506,"mean_force":0.72099,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49512,-0.12761,0.02706]},{"body_a":"world","body_b":"push_box","contact_count":1732.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49999,0.02731,0.17235]},{"body_a":"world","body_b":"push_box","contact_count":1048.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49822,0.03745,0.03535]}],"total_contact_groups":7},"final_pose_error":0.02453,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52701,-0.15548,0.02499],"final_tcp_position":[0.49616,-0.12617,0.29704],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":85.63188,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":433.0,"n_steps_budget":600.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1732.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.50089,0.05562,0.04344],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07677,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":262.0,"n_steps_budget":600.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":34.02816,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1048.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.49853,0.01812,0.03061],"tcp_start":[0.50089,0.05562,0.04344],"tcp_to_object_dist_end":0.03784,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":185.0,"n_steps_budget":1000.0,"object_pos_end":[0.52988,-0.15363,0.02804],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.03026,"object_to_goal_dist_start":0.13127,"object_z_max":0.02862,"peak_contact_force":61.23143,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":253.0,"raw_peak_contact_force":85.63188,"subtask_id":"push","tcp_end":[0.49736,-0.12645,0.02154],"tcp_start":[0.49853,0.01812,0.03061],"tcp_to_object_dist_end":0.04288,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":571.0,"n_steps_budget":600.0,"object_pos_end":[0.52701,-0.15548,0.02499],"object_pos_start":[0.52988,-0.15363,0.02804],"object_to_goal_dist_end":0.02756,"object_to_goal_dist_start":0.03026,"object_z_max":0.02822,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2173.0,"raw_peak_contact_force":2.18505,"tcp_end":[0.49616,-0.12617,0.29704],"tcp_start":[0.49736,-0.12645,0.02154],"tcp_to_object_dist_end":0.27536,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```