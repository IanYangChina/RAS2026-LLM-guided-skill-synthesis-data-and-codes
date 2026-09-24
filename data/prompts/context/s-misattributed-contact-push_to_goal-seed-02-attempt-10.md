## Search State

- **Seed**: 2
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.6483 | 0.86 | ✅ accepted |
| 9 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.5117 | 0.66 | ❌ rejected |
| 8 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.5160 | 0.69 | ✅ accepted |
| 7 | approach → align → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.2985 | 0.47 | ❌ rejected |
| 6 | approach → align → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.5070 | 0.66 | ✅ accepted |

**Proposal policy**: task_score is 0.86 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.857, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

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

## Current Skill (Q=0.648) — your mutation base

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
    - 0.025
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
      distance: 0.1
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
      - 0.05
      - 0.2
      default: 0.1
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
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.025], offset_along_axis={axis=task_goal_direction, distance=0.1, mode=replace_offset_projection, sign=negative}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_side_offset: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **push_along_goal** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.1, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_stroke_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)

## Design Metrics

- **Composite score**: 0.648
- **task_score** (E): 0.857
- **fitness_score**: 0.828  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.180

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| descend_to_table | 1.00 | 1.00 | 0.1840 |
| align_behind_object | 1.00 | 1.00 | 0.0962 |
| push_along_goal | 0.33 | 1.00 | 0.3139 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| descend_to_table | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.490, -0.016, 0.122) | (0.492, -0.018, 0.025)→(0.492, -0.018, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| align_behind_object | align | 1.00 / step_budget | (0.490, -0.016, 0.122)→(0.479, 0.051, 0.059) | (0.492, -0.018, 0.025)→(0.492, -0.018, 0.025) | 0.139→0.139 | 1.00 / 3.000 | 0.392 | 199.335 |
| push_along_goal | push | 0.33 / step_budget | (0.479, 0.051, 0.059)→(0.516, -0.245, 0.023) | (0.492, -0.018, 0.025)→(0.499, -0.133, 0.026) | 0.139→0.019 | 1.00 / 4.000 | 0.245 | 0.245 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.789
- goal_progress: 0.975
- terminal_score: 0.975
- phase_score: 0.918
- phase_breakdown.push_to_goal_score: 0.975
- phase_breakdown.reach_object_high_score: 0.786

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.941
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.975
- **Median Q (composite search score)**: 0.605
- **K-run variance**: 0.0065
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93525,"average_solve_count":139.0,"average_success_count":139.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind_object.approach_side_offset":0.10569,"descend_to_table.approach_height":0.09506,"push_along_goal.push_stroke_distance":0.1728},"optimized_scores":{"best_composite_score":0.57864,"best_fitness_score":0.75864,"best_task_score":0.815},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":564.0,"contact_point_centroid":[0.49062,-0.06111,0.04791],"force_p95":185.78149,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":199.01875,"mean_force":136.82995,"phase_index":2.0,"phase_name":"push_along_goal","phase_type":"push","tcp_position_centroid":[0.4821,-0.06053,0.05072]},{"body_a":"world","body_b":"push_box","contact_count":3240.0,"contact_point_centroid":[0.48843,-0.08221,-0.00022],"force_p95":106.83585,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":175.74367,"mean_force":24.15314,"phase_index":2.0,"phase_name":"push_along_goal","phase_type":"push","tcp_position_centroid":[0.486,-0.09317,0.04435]},{"body_a":"world","body_b":"push_box","contact_count":1264.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"descend_to_table","phase_type":"approach","tcp_position_centroid":[0.48614,-0.0101,0.22117]},{"body_a":"world","body_b":"push_box","contact_count":964.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"align_behind_object","phase_type":"align","tcp_position_centroid":[0.46003,0.01919,0.09947]}],"total_contact_groups":4},"final_pose_error":0.05979,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49591,-0.12648,0.02499],"final_tcp_position":[0.52129,-0.26119,0.02371],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":199.01875,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":316.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"descend_to_table","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":964.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object_high","tcp_end":[0.47245,-0.02096,0.1393],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11436,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":241.0,"n_steps_budget":870.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"align_behind_object","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":3804.0,"raw_peak_contact_force":199.01875,"tcp_end":[0.44884,0.06206,0.06056],"tcp_start":[0.47245,-0.02096,0.1393],"tcp_to_object_dist_end":0.09598,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49591,-0.12648,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.02387,"object_to_goal_dist_start":0.12903,"object_z_max":0.03486,"peak_contact_force":0.24525,"phase_name":"push_along_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1264.0,"raw_peak_contact_force":0.24534,"subtask_id":"push_to_goal","tcp_end":[0.52129,-0.26119,0.02371],"tcp_start":[0.44884,0.06206,0.06056],"tcp_to_object_dist_end":0.13709,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93525,"average_solve_count":139.0,"average_success_count":139.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind_object.approach_side_offset":0.08818,"descend_to_table.approach_height":0.07017,"push_along_goal.push_stroke_distance":0.14996},"optimized_scores":{"best_composite_score":0.60517,"best_fitness_score":0.78517,"best_task_score":0.77968},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":479.0,"contact_point_centroid":[0.47368,-0.05674,0.04766],"force_p95":191.98637,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":201.71783,"mean_force":147.94507,"phase_index":2.0,"phase_name":"push_along_goal","phase_type":"push","tcp_position_centroid":[0.46458,-0.05752,0.05145]},{"body_a":"world","body_b":"push_box","contact_count":2786.0,"contact_point_centroid":[0.48241,-0.08398,-0.00026],"force_p95":146.81852,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":196.57204,"mean_force":26.01814,"phase_index":2.0,"phase_name":"push_along_goal","phase_type":"push","tcp_position_centroid":[0.48427,-0.11485,0.04095]},{"body_a":"push_box","body_b":"link7","contact_count":48.0,"contact_point_centroid":[0.52777,-0.10668,0.07741],"force_p95":20.98707,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.16192,"mean_force":10.22542,"phase_index":2.0,"phase_name":"push_along_goal","phase_type":"push","tcp_position_centroid":[0.49691,-0.14482,0.03959]},{"body_a":"world","body_b":"push_box","contact_count":1480.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"descend_to_table","phase_type":"approach","tcp_position_centroid":[0.47665,-0.01353,0.20853]},{"body_a":"world","body_b":"push_box","contact_count":720.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"align_behind_object","phase_type":"align","tcp_position_centroid":[0.43672,0.00141,0.08673]}],"total_contact_groups":5},"final_pose_error":0.01987,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5042,-0.12202,0.02499],"final_tcp_position":[0.54768,-0.2723,0.01932],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":201.71783,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":370.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"descend_to_table","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":720.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object_high","tcp_end":[0.45313,-0.02789,0.11443],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08956,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":180.0,"n_steps_budget":690.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"align_behind_object","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":3313.0,"raw_peak_contact_force":201.71783,"tcp_end":[0.42086,0.03338,0.05972],"tcp_start":[0.45313,-0.02789,0.11443],"tcp_to_object_dist_end":0.07932,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":969.0,"n_steps_budget":1000.0,"object_pos_end":[0.5042,-0.12202,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.0283,"object_to_goal_dist_start":0.12843,"object_z_max":0.04141,"peak_contact_force":0.24525,"phase_name":"push_along_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1480.0,"raw_peak_contact_force":0.24534,"subtask_id":"push_to_goal","tcp_end":[0.54768,-0.2723,0.01932],"tcp_start":[0.42086,0.03338,0.05972],"tcp_to_object_dist_end":0.15655,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92913,"average_solve_count":127.0,"average_success_count":127.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind_object.approach_side_offset":0.07651,"descend_to_table.approach_height":0.07037,"push_along_goal.push_stroke_distance":0.11028},"optimized_scores":{"best_composite_score":0.76095,"best_fitness_score":0.94095,"best_task_score":0.97503},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":2402.0,"contact_point_centroid":[0.5425,-0.08376,-0.00048],"force_p95":174.86494,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":197.26761,"mean_force":49.98566,"phase_index":2.0,"phase_name":"push_along_goal","phase_type":"push","tcp_position_centroid":[0.53056,-0.06752,0.04859]},{"body_a":"attachment","body_b":"push_box","contact_count":846.0,"contact_point_centroid":[0.53593,-0.07941,0.04697],"force_p95":191.98274,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":196.00672,"mean_force":139.6673,"phase_index":2.0,"phase_name":"push_along_goal","phase_type":"push","tcp_position_centroid":[0.52794,-0.07682,0.04819]},{"body_a":"push_box","body_b":"link7","contact_count":50.0,"contact_point_centroid":[0.51789,-0.15788,0.06575],"force_p95":17.52802,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.75558,"mean_force":9.01042,"phase_index":2.0,"phase_name":"push_along_goal","phase_type":"push","tcp_position_centroid":[0.48707,-0.18451,0.03187]},{"body_a":"world","body_b":"push_box","contact_count":1524.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"descend_to_table","phase_type":"approach","tcp_position_centroid":[0.52087,0.00054,0.20783]},{"body_a":"world","body_b":"push_box","contact_count":744.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"align_behind_object","phase_type":"align","tcp_position_centroid":[0.55464,0.02858,0.08399]}],"total_contact_groups":5},"final_pose_error":0.0558,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49749,-0.1513,0.02784],"final_tcp_position":[0.47924,-0.20058,0.02742],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":197.26761,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":381.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"descend_to_table","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":744.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object_high","tcp_end":[0.54412,0.00112,0.11297],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08845,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":186.0,"n_steps_budget":660.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":0.6857,"phase_name":"align_behind_object","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":3298.0,"raw_peak_contact_force":197.26761,"tcp_end":[0.56782,0.05823,0.05686],"tcp_start":[0.54412,0.00112,0.11297],"tcp_to_object_dist_end":0.06682,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49749,-0.1513,0.02784],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.00401,"object_to_goal_dist_start":0.16043,"object_z_max":0.04029,"peak_contact_force":0.24525,"phase_name":"push_along_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1524.0,"raw_peak_contact_force":0.24534,"subtask_id":"push_to_goal","tcp_end":[0.47924,-0.20058,0.02742],"tcp_start":[0.56782,0.05823,0.05686],"tcp_to_object_dist_end":0.05256,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```