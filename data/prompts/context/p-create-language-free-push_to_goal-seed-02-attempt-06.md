## Search State

- **Seed**: 2
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.3478 | 0.48 | ❌ rejected |
| 5 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.5642 | 0.70 | ❌ rejected |
| 4 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.6401 | 0.80 | ❌ rejected |
| 3 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.1749 | 0.59 | ❌ rejected |
| 2 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.6412 | 0.80 | ✅ accepted |

**Proposal policy**: task_score is 0.48 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.801, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.348) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: pre_contact
  anchor: object
  offset:
  - 0.0
  - 0.05
  - 0.0
  weight: 0.3
- id: reach_goal
  target_entity: object
  metric: goal_progress
  weight: 0.7
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
    - 0.05
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: pre_contact
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: push_box
    offset:
    - 0.0
    - 0.05
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  subtask_id: pre_contact
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
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 10.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: pre_contact
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
    push_distance:
      type: scalar
      range:
      - 0.08
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: goal_marker
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.05, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.05, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.15, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=task_goal, entity=goal_marker, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.348
- **task_score** (E): 0.476
- **fitness_score**: 0.538  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.390

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1624 |
| descend_1 | 1.00 | 1.00 | 0.0993 |
| contact_1 | 1.00 | 1.00 | 0.0001 |
| push_1 | 1.00 | 1.00 | 0.1853 |
| retract_1 | 1.00 | 1.00 | 0.0857 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.490, 0.006, 0.144) | (0.492, -0.018, 0.025)→(0.492, -0.018, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_1 | descend | 1.00 / step_budget | (0.490, 0.006, 0.144)→(0.494, 0.008, 0.045) | (0.492, -0.018, 0.025)→(0.494, -0.017, 0.024) | 0.139→0.140 | 1.00 / 4.000 | 276.419 | 283.633 |
| contact_1 | contact | 1.00 / force_exceeded | (0.494, 0.008, 0.045)→(0.495, 0.008, 0.045) | (0.494, -0.017, 0.024)→(0.494, -0.017, 0.024) | 0.140→0.140 | 1.00 / 4.000 | 105.798 | 105.798 |
| push_1 | push | 1.00 / step_budget | (0.495, 0.008, 0.045)→(0.515, -0.168, 0.027) | (0.494, -0.017, 0.024)→(0.522, -0.089, 0.032) | 0.140→0.065 | 1.00 / 1.333 | 0.606 | 281.863 |
| retract_1 | retract | 1.00 / step_budget | (0.515, -0.168, 0.027)→(0.499, -0.152, 0.106) | (0.522, -0.089, 0.032)→(0.522, -0.080, 0.025) | 0.065→0.074 | 1.00 / 4.000 | 0.245 | 2.985 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.659
- lateral_force_integral: None
- approach_alignment: 0.803
- goal_progress: 0.520
- terminal_score: 0.520
- phase_score: 0.620
- phase_breakdown.pre_contact_score: 0.671
- phase_breakdown.reach_goal_score: 0.598

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.580
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.520
- **Median Q (composite search score)**: 0.360
- **K-run variance**: 0.0016
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.396


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89262,"average_solve_count":149.0,"average_success_count":149.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.12056,"contact_1.contact_force":5.34672,"contact_1.speed":0.03391,"push_1.push_distance":0.24561,"push_1.push_speed":0.0791,"retract_1.speed":0.08243},"optimized_scores":{"best_composite_score":0.38982,"best_fitness_score":0.57982,"best_task_score":0.52},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":155.0,"contact_point_centroid":[0.49657,-0.03416,0.04786],"force_p95":280.42751,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":294.44517,"mean_force":217.89306,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49402,-0.0427,0.04676]},{"body_a":"attachment","body_b":"push_box","contact_count":29.0,"contact_point_centroid":[0.48273,-0.00052,0.0471],"force_p95":284.29299,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":285.94687,"mean_force":237.87395,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47113,0.00126,0.04777]},{"body_a":"world","body_b":"push_box","contact_count":337.0,"contact_point_centroid":[0.50403,-0.05186,-0.00111],"force_p95":235.0127,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":243.31562,"mean_force":101.09935,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49541,-0.0616,0.04323]},{"body_a":"world","body_b":"push_box","contact_count":821.0,"contact_point_centroid":[0.47225,-0.02338,-5e-05],"force_p95":39.83676,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":219.44866,"mean_force":8.70967,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47045,0.00075,0.09358]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.48545,-0.00203,0.0451],"force_p95":105.65571,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":105.65571,"mean_force":105.65571,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47423,0.00185,0.04474]},{"body_a":"world","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.48047,-0.01633,-0.00077],"force_p95":79.23093,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":86.46398,"mean_force":35.46383,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47423,0.00185,0.04474]},{"body_a":"world","body_b":"push_box","contact_count":933.0,"contact_point_centroid":[0.52213,-0.09254,-0.0001],"force_p95":0.65455,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.2969,"mean_force":0.2998,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50444,-0.17022,0.06918]},{"body_a":"world","body_b":"push_box","contact_count":1192.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24532,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48657,0.00032,0.22409]}],"total_contact_groups":8},"final_pose_error":0.01986,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52241,-0.09226,0.02499],"final_tcp_position":[0.49902,-0.15487,0.10578],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":294.44517,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":298.0,"n_steps_budget":930.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1192.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.47301,0.00067,0.14488],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12245,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":212.0,"n_steps_budget":750.0,"object_pos_end":[0.47326,-0.0233,0.02421],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12949,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":285.94687,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":850.0,"raw_peak_contact_force":285.94687,"subtask_id":"pre_contact","tcp_end":[0.47423,0.00185,0.04474],"tcp_start":[0.47301,0.00067,0.14488],"tcp_to_object_dist_end":0.03249,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.47326,-0.02329,0.02421],"object_pos_start":[0.47326,-0.0233,0.02421],"object_to_goal_dist_end":0.1295,"object_to_goal_dist_start":0.12949,"object_z_max":0.02421,"peak_contact_force":105.65571,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4.0,"raw_peak_contact_force":105.65571,"subtask_id":"pre_contact","tcp_end":[0.47429,0.00187,0.04471],"tcp_start":[0.47423,0.00185,0.04474],"tcp_to_object_dist_end":0.03248,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":241.0,"n_steps_budget":1000.0,"object_pos_end":[0.52147,-0.10358,0.03492],"object_pos_start":[0.47326,-0.02329,0.02421],"object_to_goal_dist_end":0.05209,"object_to_goal_dist_start":0.1295,"object_z_max":0.04255,"peak_contact_force":0.71895,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":492.0,"raw_peak_contact_force":294.44517,"subtask_id":"reach_goal","tcp_end":[0.515,-0.19015,0.02581],"tcp_start":[0.47429,0.00187,0.04471],"tcp_to_object_dist_end":0.08729,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":273.0,"n_steps_budget":840.0,"object_pos_end":[0.52241,-0.09226,0.02499],"object_pos_start":[0.52147,-0.10358,0.03492],"object_to_goal_dist_end":0.06193,"object_to_goal_dist_start":0.05209,"object_z_max":0.03492,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":933.0,"raw_peak_contact_force":3.2969,"tcp_end":[0.49902,-0.15487,0.10578],"tcp_start":[0.515,-0.19015,0.02581],"tcp_to_object_dist_end":0.10485,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.97037,"average_solve_count":135.0,"average_success_count":135.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.1442,"contact_1.contact_force":8.0139,"contact_1.speed":0.02475,"push_1.push_distance":0.24293,"push_1.push_speed":0.09469,"retract_1.speed":0.0797},"optimized_scores":{"best_composite_score":0.36005,"best_fitness_score":0.55005,"best_task_score":0.48299},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":143.0,"contact_point_centroid":[0.47866,-0.04137,0.04802],"force_p95":314.53331,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":344.60671,"mean_force":217.37983,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48171,-0.04759,0.04595]},{"body_a":"attachment","body_b":"push_box","contact_count":28.0,"contact_point_centroid":[0.4622,-0.00769,0.04708],"force_p95":290.50286,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":292.1558,"mean_force":241.92605,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45059,-0.00593,0.04775]},{"body_a":"world","body_b":"push_box","contact_count":312.0,"contact_point_centroid":[0.4861,-0.05543,-0.00111],"force_p95":238.05298,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":254.11627,"mean_force":100.55427,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48631,-0.06594,0.04248]},{"body_a":"world","body_b":"push_box","contact_count":822.0,"contact_point_centroid":[0.4511,-0.03082,-5e-05],"force_p95":39.23144,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":224.85636,"mean_force":8.54529,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45102,-0.00603,0.09343]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.4647,-0.00928,0.04503],"force_p95":104.58805,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":104.58805,"mean_force":104.58805,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.45346,-0.00543,0.04465]},{"body_a":"world","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.45928,-0.02377,-0.00078],"force_p95":77.10592,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":84.02931,"mean_force":35.12923,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.45346,-0.00543,0.04465]},{"body_a":"world","body_b":"push_box","contact_count":937.0,"contact_point_centroid":[0.50672,-0.08417,-0.00012],"force_p95":0.55733,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.07749,"mean_force":0.29301,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51027,-0.16747,0.06845]},{"body_a":"world","body_b":"push_box","contact_count":1192.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24532,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47763,-0.00276,0.22338]}],"total_contact_groups":8},"final_pose_error":0.01989,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50705,-0.08397,0.02499],"final_tcp_position":[0.50064,-0.15414,0.10556],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":344.60671,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":298.0,"n_steps_budget":810.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1192.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.45461,-0.00571,0.14412],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12199,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":212.0,"n_steps_budget":750.0,"object_pos_end":[0.45207,-0.03076,0.0242],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12852,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":292.1558,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":850.0,"raw_peak_contact_force":292.1558,"subtask_id":"pre_contact","tcp_end":[0.45346,-0.00543,0.04465],"tcp_start":[0.45461,-0.00571,0.14412],"tcp_to_object_dist_end":0.03258,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.45208,-0.03075,0.0242],"object_pos_start":[0.45207,-0.03076,0.0242],"object_to_goal_dist_end":0.12852,"object_to_goal_dist_start":0.12852,"object_z_max":0.0242,"peak_contact_force":104.58805,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4.0,"raw_peak_contact_force":104.58805,"subtask_id":"pre_contact","tcp_end":[0.45353,-0.00541,0.04461],"tcp_start":[0.45346,-0.00543,0.04465],"tcp_to_object_dist_end":0.03257,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":225.0,"n_steps_budget":1000.0,"object_pos_end":[0.5096,-0.09536,0.03464],"object_pos_start":[0.45208,-0.03075,0.0242],"object_to_goal_dist_end":0.05631,"object_to_goal_dist_start":0.12852,"object_z_max":0.04036,"peak_contact_force":0.71924,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":455.0,"raw_peak_contact_force":344.60671,"subtask_id":"reach_goal","tcp_end":[0.526,-0.18443,0.02566],"tcp_start":[0.45353,-0.00541,0.04461],"tcp_to_object_dist_end":0.09101,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":270.0,"n_steps_budget":870.0,"object_pos_end":[0.50705,-0.08397,0.02499],"object_pos_start":[0.5096,-0.09536,0.03464],"object_to_goal_dist_end":0.0664,"object_to_goal_dist_start":0.05631,"object_z_max":0.03464,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":937.0,"raw_peak_contact_force":4.07749,"tcp_end":[0.50064,-0.15414,0.10556],"tcp_start":[0.526,-0.18443,0.02566],"tcp_to_object_dist_end":0.10703,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.32161,"average_solve_count":199.0,"average_success_count":199.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.11931,"contact_1.contact_force":8.0532,"contact_1.speed":0.02516,"push_1.push_distance":0.21358,"push_1.push_speed":0.02115,"retract_1.speed":0.11096},"optimized_scores":{"best_composite_score":0.29344,"best_fitness_score":0.48344,"best_task_score":0.42427},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":39.0,"contact_point_centroid":[0.5625,0.02391,0.04691],"force_p95":258.70787,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":272.79589,"mean_force":227.84025,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.55099,0.02618,0.04751]},{"body_a":"world","body_b":"push_box","contact_count":802.0,"contact_point_centroid":[0.55444,0.00252,-7e-05],"force_p95":40.90117,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":236.78515,"mean_force":11.43928,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.54547,0.02424,0.09045]},{"body_a":"attachment","body_b":"push_box","contact_count":196.0,"contact_point_centroid":[0.55842,-0.01246,0.04924],"force_p95":198.34008,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":206.5378,"mean_force":149.9117,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.55059,-0.01826,0.0493]},{"body_a":"world","body_b":"push_box","contact_count":519.0,"contact_point_centroid":[0.55137,-0.02698,-0.00064],"force_p95":108.22531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":143.82661,"mean_force":57.17241,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.54631,-0.0236,0.04683]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.56682,0.02272,0.0452],"force_p95":107.15166,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":107.15166,"mean_force":107.15166,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5558,0.02716,0.0449]},{"body_a":"world","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.56286,0.00933,-0.0008],"force_p95":84.16312,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":92.42442,"mean_force":35.8671,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5558,0.02716,0.0449]},{"body_a":"world","body_b":"push_box","contact_count":934.0,"contact_point_centroid":[0.53637,-0.06611,-8e-05],"force_p95":0.33214,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.57986,"mean_force":0.26418,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49816,-0.13791,0.06782]},{"body_a":"world","body_b":"push_box","contact_count":1308.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52066,0.01103,0.22221]}],"total_contact_groups":8},"final_pose_error":0.02,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5367,-0.06525,0.02499],"final_tcp_position":[0.49721,-0.14594,0.10562],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":272.79589,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":327.0,"n_steps_budget":990.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1308.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.54365,0.02279,0.14217],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.1195,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":210.0,"n_steps_budget":750.0,"object_pos_end":[0.55575,0.00254,0.02423],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16241,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":251.15515,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":841.0,"raw_peak_contact_force":272.79589,"subtask_id":"pre_contact","tcp_end":[0.5558,0.02716,0.0449],"tcp_start":[0.54365,0.02279,0.14217],"tcp_to_object_dist_end":0.03215,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.55573,0.00254,0.02424],"object_pos_start":[0.55575,0.00254,0.02423],"object_to_goal_dist_end":0.1624,"object_to_goal_dist_start":0.16241,"object_z_max":0.02423,"peak_contact_force":107.15166,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4.0,"raw_peak_contact_force":107.15166,"subtask_id":"pre_contact","tcp_end":[0.55585,0.02717,0.04494],"tcp_start":[0.5558,0.02716,0.0449],"tcp_to_object_dist_end":0.03218,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":247.0,"n_steps_budget":1000.0,"object_pos_end":[0.53444,-0.06947,0.0274],"object_pos_start":[0.55573,0.00254,0.02424],"object_to_goal_dist_end":0.08762,"object_to_goal_dist_start":0.1624,"object_z_max":0.03564,"peak_contact_force":0.37992,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":715.0,"raw_peak_contact_force":206.5378,"subtask_id":"reach_goal","tcp_end":[0.50274,-0.12792,0.02888],"tcp_start":[0.55585,0.02717,0.04494],"tcp_to_object_dist_end":0.06652,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":246.0,"n_steps_budget":600.0,"object_pos_end":[0.5367,-0.06525,0.02499],"object_pos_start":[0.53444,-0.06947,0.0274],"object_to_goal_dist_end":0.09236,"object_to_goal_dist_start":0.08762,"object_z_max":0.02744,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":934.0,"raw_peak_contact_force":1.57986,"tcp_end":[0.49721,-0.14594,0.10562],"tcp_start":[0.50274,-0.12792,0.02888],"tcp_to_object_dist_end":0.12072,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```