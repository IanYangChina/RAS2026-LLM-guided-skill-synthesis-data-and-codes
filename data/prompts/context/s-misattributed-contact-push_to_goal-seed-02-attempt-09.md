## Search State

- **Seed**: 2
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.5117 | 0.66 | ❌ rejected |
| 8 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.5160 | 0.69 | ✅ accepted |
| 7 | approach → align → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.2985 | 0.47 | ❌ rejected |
| 6 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.5070 | 0.66 | ✅ accepted |
| 5 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.4979 | 0.66 | ✅ accepted |

**Proposal policy**: task_score is 0.66 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position (0.47139345610991795, -0.0241810627903052, 0.025) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, -0.15, 0.025) | final destination targets |
| `fixture` | offset from fixture pose (if defined, else world) | targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=0.512) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: reach_object_high
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.08
  weight: 0.3
- id: push_to_goal
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: descend_to_table
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
    - 0.08
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.03
      - 0.15
      default: 0.08
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_object_high
- id: align_behind_object
  type: align
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
      mode: replace_offset_projection
      sign: negative
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_side_offset:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
- id: push_along_goal
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.15
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_stroke_distance:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  subtask_id: push_to_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **descend_to_table** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.08], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **align_behind_object** (`align`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.1, mode=replace_offset_projection, sign=negative}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_side_offset: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **push_along_goal** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.15, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_stroke_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)

## Design Metrics

- **Composite score**: 0.512
- **task_score** (E): 0.656
- **fitness_score**: 0.692  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.180

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| descend_to_table | 1.00 | 1.00 | 0.2037 |
| align_behind_object | 1.00 | 1.00 | 0.1625 |
| push_along_goal | 0.67 | 1.00 | 0.3874 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| descend_to_table | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.490, -0.016, 0.102) | (0.492, -0.018, 0.025)→(0.492, -0.018, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| align_behind_object | align | 1.00 / step_budget | (0.490, -0.016, 0.102)→(0.468, 0.119, 0.029) | (0.492, -0.018, 0.025)→(0.492, -0.018, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 78.009 |
| push_along_goal | push | 0.67 / step_budget | (0.468, 0.119, 0.029)→(0.496, -0.248, 0.020) | (0.492, -0.018, 0.025)→(0.478, -0.165, 0.025) | 0.139→0.047 | 1.00 / 4.000 | 0.245 | 0.245 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.856
- goal_progress: 0.730
- terminal_score: 0.730
- phase_score: 0.762
- phase_breakdown.push_to_goal_score: 0.730
- phase_breakdown.reach_object_high_score: 0.836

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.750
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.730
- **Median Q (composite search score)**: 0.498
- **K-run variance**: 0.0018
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.339


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.94706,"average_solve_count":170.0,"average_success_count":170.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind_object.approach_side_offset":0.19288,"descend_to_table.approach_height":0.05053,"push_along_goal.push_stroke_distance":0.29751},"optimized_scores":{"best_composite_score":0.4672,"best_fitness_score":0.6472,"best_task_score":0.61003},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":205.0,"contact_point_centroid":[0.49912,-0.02517,0.051],"force_p95":47.92596,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":56.97627,"mean_force":21.3998,"phase_index":2.0,"phase_name":"push_along_goal","phase_type":"push","tcp_position_centroid":[0.45919,0.00788,0.02401]},{"body_a":"world","body_b":"push_box","contact_count":2555.0,"contact_point_centroid":[0.46293,-0.08848,-4e-05],"force_p95":12.53031,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":52.42112,"mean_force":2.24126,"phase_index":2.0,"phase_name":"push_along_goal","phase_type":"push","tcp_position_centroid":[0.47041,-0.04455,0.02264]},{"body_a":"attachment","body_b":"push_box","contact_count":211.0,"contact_point_centroid":[0.47218,-0.0795,0.02476],"force_p95":10.68919,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.55975,"mean_force":2.73283,"phase_index":2.0,"phase_name":"push_along_goal","phase_type":"push","tcp_position_centroid":[0.4762,-0.06866,0.02262]},{"body_a":"world","body_b":"push_box","contact_count":1596.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"descend_to_table","phase_type":"approach","tcp_position_centroid":[0.4855,-0.01047,0.19903]},{"body_a":"world","body_b":"push_box","contact_count":1628.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"align_behind_object","phase_type":"align","tcp_position_centroid":[0.44937,0.06055,0.06006]}],"total_contact_groups":5},"final_pose_error":0.21573,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.44981,-0.15352,0.02499],"final_tcp_position":[0.51345,-0.23092,0.01992],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":56.97627,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":399.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"descend_to_table","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1628.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object_high","tcp_end":[0.47143,-0.02154,0.09522],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07028,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":407.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"align_behind_object","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2971.0,"raw_peak_contact_force":56.97627,"tcp_end":[0.42956,0.14431,0.02793],"tcp_start":[0.47143,-0.02154,0.09522],"tcp_to_object_dist_end":0.17363,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.44981,-0.15352,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.05032,"object_to_goal_dist_start":0.12903,"object_z_max":0.03413,"peak_contact_force":0.24525,"phase_name":"push_along_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1596.0,"raw_peak_contact_force":0.24534,"subtask_id":"push_to_goal","tcp_end":[0.51345,-0.23092,0.01992],"tcp_start":[0.42956,0.14431,0.02793],"tcp_to_object_dist_end":0.10033,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.94479,"average_solve_count":163.0,"average_success_count":163.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind_object.approach_side_offset":0.17186,"descend_to_table.approach_height":0.06148,"push_along_goal.push_stroke_distance":0.11082},"optimized_scores":{"best_composite_score":0.4983,"best_fitness_score":0.6783,"best_task_score":0.62643},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":279.0,"contact_point_centroid":[0.4854,-0.03621,0.05057],"force_p95":91.18563,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":105.78439,"mean_force":55.97232,"phase_index":2.0,"phase_name":"push_along_goal","phase_type":"push","tcp_position_centroid":[0.44164,-0.01294,0.02722]},{"body_a":"world","body_b":"push_box","contact_count":2689.0,"contact_point_centroid":[0.45772,-0.09628,-7e-05],"force_p95":52.36773,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":74.69172,"mean_force":6.91791,"phase_index":2.0,"phase_name":"push_along_goal","phase_type":"push","tcp_position_centroid":[0.45798,-0.05881,0.02429]},{"body_a":"attachment","body_b":"push_box","contact_count":240.0,"contact_point_centroid":[0.46811,-0.08647,0.03096],"force_p95":32.88588,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.24998,"mean_force":9.94484,"phase_index":2.0,"phase_name":"push_along_goal","phase_type":"push","tcp_position_centroid":[0.46702,-0.07507,0.02504]},{"body_a":"world","body_b":"push_box","contact_count":1544.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"descend_to_table","phase_type":"approach","tcp_position_centroid":[0.47648,-0.01361,0.20426]},{"body_a":"world","body_b":"push_box","contact_count":1420.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"align_behind_object","phase_type":"align","tcp_position_centroid":[0.42013,0.03917,0.06719]}],"total_contact_groups":5},"final_pose_error":0.03077,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.45349,-0.1618,0.02499],"final_tcp_position":[0.52807,-0.2259,0.01898],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":105.78439,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":386.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"descend_to_table","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1420.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object_high","tcp_end":[0.45285,-0.02803,0.10581],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08094,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":355.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"align_behind_object","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":3208.0,"raw_peak_contact_force":105.78439,"tcp_end":[0.38874,0.10852,0.03085],"tcp_start":[0.45285,-0.02803,0.10581],"tcp_to_object_dist_end":0.15313,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45349,-0.1618,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.04798,"object_to_goal_dist_start":0.12843,"object_z_max":0.03615,"peak_contact_force":0.24525,"phase_name":"push_along_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1544.0,"raw_peak_contact_force":0.24534,"subtask_id":"push_to_goal","tcp_end":[0.52807,-0.2259,0.01898],"tcp_start":[0.38874,0.10852,0.03085],"tcp_to_object_dist_end":0.09852,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.94578,"average_solve_count":166.0,"average_success_count":166.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind_object.approach_side_offset":0.12694,"descend_to_table.approach_height":0.06278,"push_along_goal.push_stroke_distance":0.1789},"optimized_scores":{"best_composite_score":0.56952,"best_fitness_score":0.74952,"best_task_score":0.73049},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":221.0,"contact_point_centroid":[0.54417,-0.1182,0.05347],"force_p95":64.49099,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":71.2674,"mean_force":33.27243,"phase_index":2.0,"phase_name":"push_along_goal","phase_type":"push","tcp_position_centroid":[0.50317,-0.12567,0.02272]},{"body_a":"world","body_b":"push_box","contact_count":2302.0,"contact_point_centroid":[0.54607,-0.10209,-0.00012],"force_p95":27.66755,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":54.29342,"mean_force":4.49891,"phase_index":2.0,"phase_name":"push_along_goal","phase_type":"push","tcp_position_centroid":[0.51283,-0.09592,0.02224]},{"body_a":"attachment","body_b":"push_box","contact_count":262.0,"contact_point_centroid":[0.54196,-0.05341,0.04315],"force_p95":33.99773,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.61486,"mean_force":8.80694,"phase_index":2.0,"phase_name":"push_along_goal","phase_type":"push","tcp_position_centroid":[0.5304,-0.04332,0.0222]},{"body_a":"world","body_b":"push_box","contact_count":1580.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"descend_to_table","phase_type":"approach","tcp_position_centroid":[0.52095,0.00055,0.20403]},{"body_a":"world","body_b":"push_box","contact_count":1244.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"align_behind_object","phase_type":"align","tcp_position_centroid":[0.56293,0.05214,0.06551]}],"total_contact_groups":5},"final_pose_error":0.03301,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53107,-0.18006,0.02499],"final_tcp_position":[0.4474,-0.28686,0.01996],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":71.2674,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":395.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"descend_to_table","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1244.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object_high","tcp_end":[0.54424,0.00112,0.10549],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.081,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":311.0,"n_steps_budget":960.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":0.24522,"phase_name":"align_behind_object","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2785.0,"raw_peak_contact_force":71.2674,"tcp_end":[0.58461,0.10487,0.02872],"tcp_start":[0.54424,0.00112,0.10549],"tcp_to_object_dist_end":0.10824,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53107,-0.18006,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.04324,"object_to_goal_dist_start":0.16043,"object_z_max":0.03534,"peak_contact_force":0.24525,"phase_name":"push_along_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1580.0,"raw_peak_contact_force":0.24534,"subtask_id":"push_to_goal","tcp_end":[0.4474,-0.28686,0.01996],"tcp_start":[0.58461,0.10487,0.02872],"tcp_to_object_dist_end":0.13576,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```