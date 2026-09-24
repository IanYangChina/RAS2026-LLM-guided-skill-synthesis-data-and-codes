## Search State

- **Seed**: 2
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → align → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.2985 | 0.47 | ❌ rejected |
| 6 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.5070 | 0.66 | ✅ accepted |
| 5 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.4979 | 0.66 | ✅ accepted |
| 4 | align → align → pull | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 0 | 0.5405 | 0.57 | ❌ rejected |
| 3 | align → align → pull | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 0 | 0.5405 | 0.57 | ❌ rejected |

**Proposal policy**: task_score is 0.47 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.298) — your mutation base

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

- **Composite score**: 0.298
- **task_score** (E): 0.474
- **fitness_score**: 0.508  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| descend_to_table | 1.00 | 1.00 | 0.2050 |
| align_behind_high | 1.00 | 1.00 | 0.1229 |
| descend_to_contact | 1.00 | 1.00 | 0.0626 |
| push_along_goal | 0.67 | 1.00 | 0.3829 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| descend_to_table | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.489, -0.016, 0.101) | (0.492, -0.018, 0.025)→(0.492, -0.018, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| align_behind_high | align | 1.00 / step_budget | (0.489, -0.016, 0.101)→(0.471, 0.097, 0.100) | (0.492, -0.018, 0.025)→(0.492, -0.018, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_to_contact | descend | 1.00 / step_budget | (0.471, 0.097, 0.100)→(0.476, 0.081, 0.042) | (0.492, -0.018, 0.025)→(0.492, -0.018, 0.025) | 0.139→0.139 | 1.00 / 3.333 | 0.327 | 94.836 |
| push_along_goal | push | 0.67 / step_budget | (0.476, 0.081, 0.042)→(0.503, -0.281, 0.021) | (0.492, -0.018, 0.025)→(0.522, -0.204, 0.028) | 0.139→0.069 | 1.00 / 4.000 | 0.245 | 0.245 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.987
- lateral_force_integral: None
- approach_alignment: 0.863
- goal_progress: 0.854
- terminal_score: 0.854
- phase_score: 0.844
- phase_breakdown.push_to_goal_score: 0.854
- phase_breakdown.reach_object_high_score: 0.821

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.848
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.854
- **Median Q (composite search score)**: 0.205
- **K-run variance**: 0.0616
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.310


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93064,"average_solve_count":173.0,"average_success_count":173.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind_high.approach_side_offset":0.13643,"descend_to_table.approach_height":0.08234,"push_along_goal.push_stroke_distance":0.25406},"optimized_scores":{"best_composite_score":0.05204,"best_fitness_score":0.26204,"best_task_score":0.17891},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1901.0,"contact_point_centroid":[0.51558,-0.12054,-0.00014],"force_p95":60.12428,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":154.01407,"mean_force":10.57975,"phase_index":3.0,"phase_name":"push_along_goal","phase_type":"push","tcp_position_centroid":[0.48109,-0.08947,0.0331]},{"body_a":"push_box","body_b":"link7","contact_count":268.0,"contact_point_centroid":[0.55474,-0.20736,0.05287],"force_p95":82.97862,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":98.9813,"mean_force":48.04279,"phase_index":3.0,"phase_name":"push_along_goal","phase_type":"push","tcp_position_centroid":[0.51208,-0.21761,0.02855]},{"body_a":"attachment","body_b":"push_box","contact_count":460.0,"contact_point_centroid":[0.50683,-0.13337,0.05008],"force_p95":56.63721,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":91.88559,"mean_force":16.51813,"phase_index":3.0,"phase_name":"push_along_goal","phase_type":"push","tcp_position_centroid":[0.48971,-0.12618,0.0314]},{"body_a":"world","body_b":"push_box","contact_count":1356.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"descend_to_table","phase_type":"approach","tcp_position_centroid":[0.48597,-0.0102,0.21507]},{"body_a":"world","body_b":"push_box","contact_count":1064.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"align_behind_high","phase_type":"align","tcp_position_centroid":[0.45662,0.03281,0.11404]},{"body_a":"world","body_b":"push_box","contact_count":516.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.4432,0.08394,0.07503]}],"total_contact_groups":6},"final_pose_error":0.10207,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.56647,-0.23186,0.03526],"final_tcp_position":[0.53007,-0.29913,0.02273],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":154.01407,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":339.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"descend_to_table","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1064.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object_high","tcp_end":[0.47218,-0.02111,0.12703],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10209,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":266.0,"n_steps_budget":870.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"align_behind_high","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":516.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.44281,0.0891,0.10413],"tcp_start":[0.47218,-0.02111,0.12703],"tcp_to_object_dist_end":0.14112,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":129.0,"n_steps_budget":600.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":0.4891,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2629.0,"raw_peak_contact_force":154.01407,"subtask_id":"push_to_goal","tcp_end":[0.44451,0.07738,0.04351],"tcp_start":[0.44281,0.0891,0.10413],"tcp_to_object_dist_end":0.10668,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56647,-0.23186,0.03526],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.10595,"object_to_goal_dist_start":0.12903,"object_z_max":0.03527,"peak_contact_force":0.24525,"phase_name":"push_along_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1356.0,"raw_peak_contact_force":0.24534,"subtask_id":"push_to_goal","tcp_end":[0.53007,-0.29913,0.02273],"tcp_start":[0.44451,0.07738,0.04351],"tcp_to_object_dist_end":0.0775,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93407,"average_solve_count":182.0,"average_success_count":182.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind_high.approach_side_offset":0.17286,"descend_to_table.approach_height":0.03027,"push_along_goal.push_stroke_distance":0.12127},"optimized_scores":{"best_composite_score":0.2051,"best_fitness_score":0.4151,"best_task_score":0.3874},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":348.0,"contact_point_centroid":[0.47629,-0.09721,0.04027],"force_p95":39.23407,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":74.0199,"mean_force":7.81285,"phase_index":3.0,"phase_name":"push_along_goal","phase_type":"push","tcp_position_centroid":[0.46788,-0.08534,0.02786]},{"body_a":"world","body_b":"push_box","contact_count":1991.0,"contact_point_centroid":[0.46782,-0.13062,-6e-05],"force_p95":10.28431,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":61.0897,"mean_force":1.77558,"phase_index":3.0,"phase_name":"push_along_goal","phase_type":"push","tcp_position_centroid":[0.46925,-0.08857,0.02765]},{"body_a":"push_box","body_b":"link7","contact_count":22.0,"contact_point_centroid":[0.49525,-0.07193,0.05118],"force_p95":15.16167,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.22392,"mean_force":6.19251,"phase_index":3.0,"phase_name":"push_along_goal","phase_type":"push","tcp_position_centroid":[0.45461,-0.05454,0.02948]},{"body_a":"world","body_b":"push_box","contact_count":1780.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"descend_to_table","phase_type":"approach","tcp_position_centroid":[0.47588,-0.0139,0.18845]},{"body_a":"world","body_b":"push_box","contact_count":1440.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"align_behind_high","phase_type":"align","tcp_position_centroid":[0.41902,0.03991,0.08443]},{"body_a":"world","body_b":"push_box","contact_count":640.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.39491,0.092,0.06925]}],"total_contact_groups":6},"final_pose_error":0.01997,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47508,-0.22463,0.02499],"final_tcp_position":[0.5365,-0.24596,0.01882],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":74.0199,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":445.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"descend_to_table","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1440.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object_high","tcp_end":[0.4519,-0.02848,0.07451],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.04965,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":360.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"align_behind_high","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":640.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.38826,0.11,0.09825],"tcp_start":[0.4519,-0.02848,0.07451],"tcp_to_object_dist_end":0.17106,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":160.0,"n_steps_budget":600.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2361.0,"raw_peak_contact_force":74.0199,"subtask_id":"push_to_goal","tcp_end":[0.40323,0.07181,0.0389],"tcp_start":[0.38826,0.11,0.09825],"tcp_to_object_dist_end":0.11444,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":932.0,"n_steps_budget":1000.0,"object_pos_end":[0.47508,-0.22463,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.07868,"object_to_goal_dist_start":0.12843,"object_z_max":0.02758,"peak_contact_force":0.24525,"phase_name":"push_along_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1780.0,"raw_peak_contact_force":0.24534,"subtask_id":"push_to_goal","tcp_end":[0.5365,-0.24596,0.01882],"tcp_start":[0.40323,0.07181,0.0389],"tcp_to_object_dist_end":0.06531,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92778,"average_solve_count":180.0,"average_success_count":180.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind_high.approach_side_offset":0.11276,"descend_to_table.approach_height":0.0579,"push_along_goal.push_stroke_distance":0.17877},"optimized_scores":{"best_composite_score":0.63827,"best_fitness_score":0.84827,"best_task_score":0.85428},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":402.0,"contact_point_centroid":[0.53499,-0.07707,0.0503],"force_p95":38.24408,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":56.47253,"mean_force":10.12514,"phase_index":3.0,"phase_name":"push_along_goal","phase_type":"push","tcp_position_centroid":[0.52186,-0.06925,0.03162]},{"body_a":"world","body_b":"push_box","contact_count":2476.0,"contact_point_centroid":[0.53817,-0.10798,-6e-05],"force_p95":19.72177,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":53.62534,"mean_force":3.16632,"phase_index":3.0,"phase_name":"push_along_goal","phase_type":"push","tcp_position_centroid":[0.50185,-0.12767,0.02873]},{"body_a":"push_box","body_b":"link7","contact_count":128.0,"contact_point_centroid":[0.54455,-0.11196,0.05837],"force_p95":44.84452,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.75405,"mean_force":24.82085,"phase_index":3.0,"phase_name":"push_along_goal","phase_type":"push","tcp_position_centroid":[0.50452,-0.12125,0.02989]},{"body_a":"world","body_b":"push_box","contact_count":1616.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"descend_to_table","phase_type":"approach","tcp_position_centroid":[0.52098,0.00055,0.20166]},{"body_a":"world","body_b":"push_box","contact_count":1092.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"align_behind_high","phase_type":"align","tcp_position_centroid":[0.56108,0.04642,0.09709]},{"body_a":"world","body_b":"push_box","contact_count":416.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.58043,0.09342,0.07251]}],"total_contact_groups":6},"final_pose_error":0.02076,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52303,-0.15403,0.02499],"final_tcp_position":[0.44342,-0.29858,0.02047],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":56.47253,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":404.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"descend_to_table","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1092.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object_high","tcp_end":[0.54432,0.00113,0.10064],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07616,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":273.0,"n_steps_budget":750.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"align_behind_high","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":416.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.58053,0.09222,0.09783],"tcp_start":[0.54432,0.00113,0.10064],"tcp_to_object_dist_end":0.11963,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":104.0,"n_steps_budget":600.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3006.0,"raw_peak_contact_force":56.47253,"subtask_id":"push_to_goal","tcp_end":[0.58102,0.09406,0.04408],"tcp_start":[0.58053,0.09222,0.09783],"tcp_to_object_dist_end":0.09866,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52303,-0.15403,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.02338,"object_to_goal_dist_start":0.16043,"object_z_max":0.03107,"peak_contact_force":0.24525,"phase_name":"push_along_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1616.0,"raw_peak_contact_force":0.24534,"subtask_id":"push_to_goal","tcp_end":[0.44342,-0.29858,0.02047],"tcp_start":[0.58102,0.09406,0.04408],"tcp_to_object_dist_end":0.16508,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```