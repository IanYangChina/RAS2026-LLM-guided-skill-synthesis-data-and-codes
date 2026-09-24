## Search State

- **Seed**: 0
- **Iteration**: 1 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 0 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 2 | 0.8232 | 0.76 | ✅ accepted |

**Proposal policy**: task_score is 0.76 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.823) — your mutation base

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
    - 0.03
    - 0.0
    offset_along_axis:
      distance: 0.15
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
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
  - target: source=yaml, anchor=task_goal, entity=goal_marker, offset=[0.0, 0.03, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.15, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.05, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.823
- **task_score** (E): 0.759
- **fitness_score**: 0.733  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.160

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2812 |
| contact_1 | 1.00 | 1.00 | 0.0405 |
| push_1 | 0.33 | 1.00 | 0.1618 |
| retract_1 | 1.00 | 1.00 | 0.1013 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.493, 0.077, 0.033) | (0.496, 0.001, 0.025)→(0.496, 0.001, 0.025) | 0.152→0.152 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / force_exceeded | (0.493, 0.077, 0.033)→(0.492, 0.038, 0.022) | (0.496, 0.001, 0.025)→(0.496, 0.001, 0.025) | 0.152→0.152 | 1.00 / 5.000 | 27.512 | 0.245 |
| push_1 | push | 0.33 / step_budget | (0.492, 0.038, 0.022)→(0.499, -0.122, 0.021) | (0.496, 0.001, 0.025)→(0.525, -0.152, 0.028) | 0.152→0.038 | 1.00 / 3.667 | 25.992 | 49.903 |
| retract_1 | retract | 1.00 / step_budget | (0.499, -0.122, 0.021)→(0.496, -0.075, 0.110) | (0.525, -0.152, 0.028)→(0.522, -0.151, 0.025) | 0.038→0.036 | 1.00 / 4.000 | 0.245 | 26.251 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.698
- goal_progress: 0.805
- terminal_score: 0.805
- phase_score: 0.834
- phase_breakdown.push_score: 0.881
- phase_breakdown.contact_score: 0.764
- phase_breakdown.approach_score: 0.820

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.822
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.805
- **Median Q (composite search score)**: 0.782
- **K-run variance**: 0.0040
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 11.0
- **Final σ (mean)**: 0.219


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.77273,"average_solve_count":132.0,"average_success_count":132.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":12.69592,"push_1.push_depth":0.02001},"optimized_scores":{"best_composite_score":0.91212,"best_fitness_score":0.82212,"best_task_score":0.80474},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":459.0,"contact_point_centroid":[0.53303,-0.09934,0.05413],"force_p95":38.61782,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.40042,"mean_force":22.75521,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49927,-0.09017,0.02024]},{"body_a":"world","body_b":"push_box","contact_count":1154.0,"contact_point_centroid":[0.53235,-0.1186,-6e-05],"force_p95":29.2411,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.62725,"mean_force":14.28703,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50112,-0.07005,0.01974]},{"body_a":"push_box","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.53468,-0.13345,0.05487],"force_p95":33.25553,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.56403,"mean_force":12.84615,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49624,-0.12939,0.02199]},{"body_a":"attachment","body_b":"push_box","contact_count":690.0,"contact_point_centroid":[0.51309,-0.07597,0.04623],"force_p95":26.36308,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.96358,"mean_force":12.17076,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50136,-0.06663,0.01956]},{"body_a":"attachment","body_b":"push_box","contact_count":49.0,"contact_point_centroid":[0.51207,-0.12981,0.05486],"force_p95":11.47624,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.26984,"mean_force":1.76114,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4944,-0.12549,0.02682]},{"body_a":"world","body_b":"push_box","contact_count":2321.0,"contact_point_centroid":[0.52466,-0.1566,-1e-05],"force_p95":0.4413,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.2323,"mean_force":0.29029,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49293,-0.10276,0.06921]},{"body_a":"world","body_b":"push_box","contact_count":3496.0,"contact_point_centroid":[0.51644,-0.02763,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50494,0.02455,0.16585]},{"body_a":"world","body_b":"push_box","contact_count":1896.0,"contact_point_centroid":[0.51644,-0.02763,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50996,0.02902,0.02519]}],"total_contact_groups":8},"final_pose_error":0.01133,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52335,-0.15601,0.02499],"final_tcp_position":[0.49312,-0.08172,0.11136],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51644,-0.02763,0.025]},"peak_contact_force":46.40042,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":874.0,"n_steps_budget":1000.0,"object_pos_end":[0.51644,-0.02763,0.02499],"object_pos_start":[0.51644,-0.02763,0.025],"object_to_goal_dist_end":0.12347,"object_to_goal_dist_start":0.12347,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3496.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.51171,0.04945,0.03319],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07766,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":474.0,"n_steps_budget":600.0,"object_pos_end":[0.51644,-0.02763,0.02499],"object_pos_start":[0.51644,-0.02763,0.02499],"object_to_goal_dist_end":0.12347,"object_to_goal_dist_start":0.12347,"object_z_max":0.02499,"peak_contact_force":26.84816,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1896.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.51153,0.00931,0.02129],"tcp_start":[0.51171,0.04945,0.03319],"tcp_to_object_dist_end":0.03745,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":794.0,"n_steps_budget":930.0,"object_pos_end":[0.52669,-0.15684,0.02936],"object_pos_start":[0.51644,-0.02763,0.02499],"object_to_goal_dist_end":0.02789,"object_to_goal_dist_start":0.12347,"object_z_max":0.0294,"peak_contact_force":29.34628,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2303.0,"raw_peak_contact_force":46.40042,"subtask_id":"push","tcp_end":[0.49649,-0.12931,0.0219],"tcp_start":[0.51153,0.00931,0.02129],"tcp_to_object_dist_end":0.04154,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.52335,-0.15601,0.02499],"object_pos_start":[0.52669,-0.15684,0.02936],"object_to_goal_dist_end":0.02411,"object_to_goal_dist_start":0.02789,"object_z_max":0.02945,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2377.0,"raw_peak_contact_force":36.56403,"tcp_end":[0.49312,-0.08172,0.11136],"tcp_start":[0.49649,-0.12931,0.0219],"tcp_to_object_dist_end":0.11787,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.7931,"average_solve_count":145.0,"average_success_count":145.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":9.01493,"push_1.push_depth":0.08833},"optimized_scores":{"best_composite_score":0.77531,"best_fitness_score":0.68531,"best_task_score":0.77296},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":568.0,"contact_point_centroid":[0.52984,-0.04884,0.05392],"force_p95":52.44103,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":64.66534,"mean_force":29.60879,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49562,-0.03975,0.02]},{"body_a":"world","body_b":"push_box","contact_count":1413.0,"contact_point_centroid":[0.52824,-0.06015,-0.0001],"force_p95":38.11026,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":47.4193,"mean_force":18.45307,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49518,-0.01349,0.01951]},{"body_a":"attachment","body_b":"push_box","contact_count":878.0,"contact_point_centroid":[0.50714,-0.01664,0.04643],"force_p95":36.37132,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.6524,"mean_force":16.52423,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49493,-0.0079,0.01927]},{"body_a":"push_box","body_b":"link7","contact_count":10.0,"contact_point_centroid":[0.53495,-0.08865,0.05481],"force_p95":36.08766,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.7909,"mean_force":11.55498,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49696,-0.08713,0.02172]},{"body_a":"attachment","body_b":"push_box","contact_count":52.0,"contact_point_centroid":[0.51322,-0.08641,0.05476],"force_p95":12.78188,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.39557,"mean_force":1.98839,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49524,-0.08331,0.02667]},{"body_a":"world","body_b":"push_box","contact_count":2311.0,"contact_point_centroid":[0.5282,-0.11262,-2e-05],"force_p95":0.47318,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.04156,"mean_force":0.29492,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49379,-0.06073,0.06905]},{"body_a":"world","body_b":"push_box","contact_count":3980.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49785,0.06389,0.16385]},{"body_a":"world","body_b":"push_box","contact_count":1828.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49549,0.10863,0.02431]}],"total_contact_groups":8},"final_pose_error":0.01131,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52679,-0.1122,0.02499],"final_tcp_position":[0.494,-0.03977,0.11103],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":64.66534,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":995.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3980.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.49751,0.12763,0.03133],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07395,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":457.0,"n_steps_budget":600.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.02499,"peak_contact_force":29.49103,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1828.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.49665,0.09103,0.02131],"tcp_start":[0.49751,0.12763,0.03133],"tcp_to_object_dist_end":0.03746,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52981,-0.11284,0.02924],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.04783,"object_to_goal_dist_start":0.20406,"object_z_max":0.02928,"peak_contact_force":42.56204,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2859.0,"raw_peak_contact_force":64.66534,"subtask_id":"push","tcp_end":[0.49737,-0.0871,0.02149],"tcp_start":[0.49665,0.09103,0.02131],"tcp_to_object_dist_end":0.04213,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.52679,-0.1122,0.02499],"object_pos_start":[0.52981,-0.11284,0.02924],"object_to_goal_dist_end":0.04633,"object_to_goal_dist_start":0.04783,"object_z_max":0.02974,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2373.0,"raw_peak_contact_force":40.7909,"tcp_end":[0.494,-0.03977,0.11103],"tcp_start":[0.49737,-0.0871,0.02149],"tcp_to_object_dist_end":0.11715,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.78261,"average_solve_count":138.0,"average_success_count":138.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":5.7309,"push_1.push_depth":0.11377},"optimized_scores":{"best_composite_score":0.7823,"best_fitness_score":0.6923,"best_task_score":0.69947},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":839.0,"contact_point_centroid":[0.48931,-0.08208,0.03909],"force_p95":18.64962,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.64213,"mean_force":4.71038,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48359,-0.07027,0.01901]},{"body_a":"world","body_b":"push_box","contact_count":1181.0,"contact_point_centroid":[0.49728,-0.12811,-5e-05],"force_p95":10.86312,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.92034,"mean_force":4.00578,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48358,-0.06992,0.01908]},{"body_a":"push_box","body_b":"link7","contact_count":46.0,"contact_point_centroid":[0.53347,-0.14442,0.0527],"force_p95":14.57126,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.67961,"mean_force":5.58313,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49949,-0.13737,0.01911]},{"body_a":"world","body_b":"push_box","contact_count":2474.0,"contact_point_centroid":[0.51723,-0.1853,-1e-05],"force_p95":0.24562,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.39662,"mean_force":0.25154,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49938,-0.12572,0.06384]},{"body_a":"push_box","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.53603,-0.16019,0.05305],"force_p95":1.17816,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.20187,"mean_force":1.00429,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5029,-0.15115,0.01924]},{"body_a":"attachment","body_b":"push_box","contact_count":14.0,"contact_point_centroid":[0.51354,-0.16141,0.05191],"force_p95":0.92717,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.01178,"mean_force":0.48309,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50199,-0.15024,0.02028]},{"body_a":"world","body_b":"push_box","contact_count":3432.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48376,0.02618,0.16621]},{"body_a":"world","body_b":"push_box","contact_count":1884.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46666,0.03231,0.02648]}],"total_contact_groups":8},"final_pose_error":0.01149,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51701,-0.18485,0.02499],"final_tcp_position":[0.4995,-0.10335,0.10852],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":38.64213,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":858.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3432.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.46921,0.05269,0.0342],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07745,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":471.0,"n_steps_budget":600.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":26.19751,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1884.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.4672,0.0128,0.02227],"tcp_start":[0.46921,0.05269,0.0342],"tcp_to_object_dist_end":0.03731,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51839,-0.18522,0.02683],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.03978,"object_to_goal_dist_start":0.12903,"object_z_max":0.02681,"peak_contact_force":6.06853,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2066.0,"raw_peak_contact_force":38.64213,"subtask_id":"push","tcp_end":[0.50293,-0.15107,0.01926],"tcp_start":[0.4672,0.0128,0.02227],"tcp_to_object_dist_end":0.03825,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.51701,-0.18485,0.02499],"object_pos_start":[0.51839,-0.18522,0.02683],"object_to_goal_dist_end":0.03878,"object_to_goal_dist_start":0.03978,"object_z_max":0.02683,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2491.0,"raw_peak_contact_force":1.39662,"tcp_end":[0.4995,-0.10335,0.10852],"tcp_start":[0.50293,-0.15107,0.01926],"tcp_to_object_dist_end":0.11801,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```