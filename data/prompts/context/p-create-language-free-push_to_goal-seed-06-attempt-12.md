## Search State

- **Seed**: 6
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.3356 | 0.90 | ✅ accepted |
| 11 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.4398 | 0.90 | ❌ rejected |
| 10 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.3338 | 0.90 | ❌ rejected |
| 9 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.3362 | 0.90 | ✅ accepted |
| 8 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.3317 | 0.90 | ✅ accepted |

**Proposal policy**: task_score is 0.90 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7`
- Frozen object start: [0.5045797221766332, -0.01880749562239939, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5045797221766332, -0.01880749562239939, 0.025)
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
  frozen_object_start: [0.5046, -0.0188, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5045797221766332, -0.01880749562239939, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0046, -0.1312, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.900, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.5045797221766332, -0.01880749562239939, 0.025) | approach/contact targets near object start |
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

## Current Skill (Q=0.336) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: reach_standoff
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.08
  weight: 0.2
- id: reach_contact
  anchor: object
  weight: 0.3
- id: push_complete
  target_entity: object
  weight: 0.5
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
    - 0.0
    - 0.08
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.3
      - 0.8
      default: 0.5
      binds_to:
      - path: generator.speed
        mode: replace
    approach_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.04
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.01
    - 0.01
    - 0.0
  subtask_id: reach_standoff
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
    - 0.0
    - 0.01
    offset_along_axis:
      distance: 0.04
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: negative
    tolerance: 0.01
    orientation:
      mode: none
  parameters:
    behind_distance:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.04
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.1
      - 0.4
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
    descend_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.01
    - 0.01
    - 0.0
  subtask_id: reach_contact
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
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.15
      - 0.5
      default: 0.25
      binds_to:
      - path: generator.speed
        mode: replace
    push_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.04
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: push_complete

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.0, 0.08], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.01, 0.01, 0.0]
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.0, 0.01], offset_along_axis={axis=task_goal_direction, distance=0.04, mode=replace_offset_projection, sign=negative}, tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - behind_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - descend_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.01, 0.01, 0.0]
- **push_1** (`push`)
  - target: source=yaml, anchor=task_goal, entity=goal_marker, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - retries: max_attempts=0, strategy=repeat

## Design Metrics

- **Composite score**: 0.336
- **task_score** (E): 0.900
- **fitness_score**: 0.716  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1819 |
| descend_1 | 1.00 | 1.00 | 0.0926 |
| push_1 | 1.00 | 1.00 | 0.2027 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.497, 0.026, 0.124) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_1 | descend | 1.00 / step_budget | (0.497, 0.026, 0.124)→(0.497, 0.070, 0.043) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.179 | 1.00 / 3.667 | 0.692 | 170.717 |
| push_1 | push | 1.00 / step_budget | (0.497, 0.070, 0.043)→(0.496, -0.131, 0.022) | (0.500, 0.029, 0.025)→(0.503, -0.167, 0.026) | 0.179→0.017 | 1.00 / 1.333 | 0.730 | 89.100 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.711
- goal_progress: 0.915
- terminal_score: 0.915
- phase_score: 0.592
- phase_breakdown.reach_contact_score: 0.400
- phase_breakdown.reach_standoff_score: 0.676
- phase_breakdown.push_complete_score: 0.673

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.721
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.915
- **Median Q (composite search score)**: 0.339
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.245


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `acf3715aaa310bcc73047d49f01e71bc863ef036ae437b7dc851a0f6d3fe40ae`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `ec1d0331416d42e6883eeb3b72499fac99c0735b785eb70ece69dc94e8044fc3`; realized-scene SHA-256: `5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50458,-0.01881,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.00458,-0.13119,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.50458,-0.01881,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.48333,"average_solve_count":60.0,"average_success_count":60.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.30621,"approach_1.approach_tolerance":0.03214,"descend_1.behind_distance":0.04452,"descend_1.descend_speed":0.10484,"descend_1.descend_tolerance":0.01794,"push_1.push_speed":0.3994,"push_1.push_tolerance":0.01861},"optimized_scores":{"best_composite_score":0.32673,"best_fitness_score":0.70673,"best_task_score":0.87302},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":28.0,"contact_point_centroid":[0.50719,0.00645,0.04903],"force_p95":141.1796,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":161.07608,"mean_force":89.20854,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50198,0.0163,0.05098]},{"body_a":"world","body_b":"push_box","contact_count":1170.0,"contact_point_centroid":[0.50479,-0.01861,-3e-05],"force_p95":11.3561,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":132.67635,"mean_force":2.40103,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50022,0.00098,0.08308]},{"body_a":"attachment","body_b":"push_box","contact_count":215.0,"contact_point_centroid":[0.50631,-0.06738,0.04379],"force_p95":71.3469,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":82.99661,"mean_force":16.2895,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49855,-0.05574,0.0306]},{"body_a":"world","body_b":"push_box","contact_count":401.0,"contact_point_centroid":[0.50621,-0.09807,-0.0002],"force_p95":35.89521,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":53.86726,"mean_force":9.30781,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49891,-0.04896,0.03168]},{"body_a":"push_box","body_b":"link7","contact_count":16.0,"contact_point_centroid":[0.5296,-0.11844,0.05384],"force_p95":5.53945,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.49487,"mean_force":1.76464,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49721,-0.10661,0.02454]},{"body_a":"world","body_b":"push_box","contact_count":1244.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50016,-0.00797,0.2136]}],"total_contact_groups":6},"final_pose_error":0.01994,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5039,-0.16619,0.02578],"final_tcp_position":[0.49716,-0.13047,0.02218],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":161.07608,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":311.0,"n_steps_budget":600.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1244.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_standoff","tcp_end":[0.50116,-0.01645,0.12444],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.09953,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":303.0,"n_steps_budget":600.0,"object_pos_end":[0.50478,-0.01925,0.02484],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13084,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":0.48294,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1198.0,"raw_peak_contact_force":161.07608,"subtask_id":"reach_contact","tcp_end":[0.50289,0.0207,0.04295],"tcp_start":[0.50116,-0.01645,0.12444],"tcp_to_object_dist_end":0.0439,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":350.0,"n_steps_budget":600.0,"object_pos_end":[0.5039,-0.16619,0.02578],"object_pos_start":[0.50478,-0.01925,0.02484],"object_to_goal_dist_end":0.01667,"object_to_goal_dist_start":0.13084,"object_z_max":0.02756,"peak_contact_force":0.48427,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":632.0,"raw_peak_contact_force":82.99661,"subtask_id":"push_complete","tcp_end":[0.49716,-0.13047,0.02218],"tcp_start":[0.50289,0.0207,0.04295],"tcp_to_object_dist_end":0.03653,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `589e611c6c27578474525e3fd29be4fb5907d8bbd5d1ca44922bfd811e342c78`; realized-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51501,0.04767,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.01501,-0.19767,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.51501,0.04767,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.48333,"average_solve_count":60.0,"average_success_count":60.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.52149,"approach_1.approach_tolerance":0.02506,"descend_1.behind_distance":0.04624,"descend_1.descend_speed":0.31027,"descend_1.descend_tolerance":0.01312,"push_1.push_speed":0.26553,"push_1.push_tolerance":0.03224},"optimized_scores":{"best_composite_score":0.33918,"best_fitness_score":0.71918,"best_task_score":0.91178},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":57.0,"contact_point_centroid":[0.52219,0.07512,0.04817],"force_p95":176.57456,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":211.27008,"mean_force":110.43502,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51528,0.08359,0.05016]},{"body_a":"world","body_b":"push_box","contact_count":1210.0,"contact_point_centroid":[0.51513,0.05025,-6e-05],"force_p95":30.80571,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":200.87506,"mean_force":5.48927,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51084,0.06271,0.08296]},{"body_a":"attachment","body_b":"push_box","contact_count":264.0,"contact_point_centroid":[0.51347,-0.04683,0.0447],"force_p95":70.01987,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":100.04945,"mean_force":12.59638,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50493,-0.03544,0.02936]},{"body_a":"world","body_b":"push_box","contact_count":520.0,"contact_point_centroid":[0.51665,-0.05276,-0.00035],"force_p95":35.31469,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":60.64166,"mean_force":7.17676,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50755,-0.00349,0.03233]},{"body_a":"push_box","body_b":"link7","contact_count":19.0,"contact_point_centroid":[0.54337,-0.04838,0.05671],"force_p95":22.19211,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.51884,"mean_force":5.38006,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50529,-0.03106,0.02966]},{"body_a":"world","body_b":"push_box","contact_count":1292.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50464,0.02029,0.21269]}],"total_contact_groups":6},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50481,-0.16678,0.02604],"final_tcp_position":[0.49785,-0.13044,0.02148],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":211.27008,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":323.0,"n_steps_budget":600.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1292.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_standoff","tcp_end":[0.51042,0.04175,0.12315],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.09845,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":334.0,"n_steps_budget":600.0,"object_pos_end":[0.51649,0.04717,0.02431],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19786,"object_to_goal_dist_start":0.19823,"object_z_max":0.02622,"peak_contact_force":1.34779,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1267.0,"raw_peak_contact_force":211.27008,"subtask_id":"reach_contact","tcp_end":[0.51725,0.0892,0.04369],"tcp_start":[0.51042,0.04175,0.12315],"tcp_to_object_dist_end":0.04628,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":465.0,"n_steps_budget":600.0,"object_pos_end":[0.50481,-0.16678,0.02604],"object_pos_start":[0.51649,0.04717,0.02431],"object_to_goal_dist_end":0.01749,"object_to_goal_dist_start":0.19786,"object_z_max":0.03215,"peak_contact_force":0.05016,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":803.0,"raw_peak_contact_force":100.04945,"subtask_id":"push_complete","tcp_end":[0.49785,-0.13044,0.02148],"tcp_start":[0.51725,0.0892,0.04369],"tcp_to_object_dist_end":0.03729,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f2c9c63f0d9eca1b3ff8bf951759f6a3adee73f9f65e1cd3613c5e9d1203ebcc`; realized-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47924,0.05847,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02076,-0.20847,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47924,0.05847,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.48333,"average_solve_count":60.0,"average_success_count":60.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.44107,"approach_1.approach_tolerance":0.02142,"descend_1.behind_distance":0.04915,"descend_1.descend_speed":0.23809,"descend_1.descend_tolerance":0.01054,"push_1.push_speed":0.36086,"push_1.push_tolerance":0.02412},"optimized_scores":{"best_composite_score":0.34092,"best_fitness_score":0.72092,"best_task_score":0.91481},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":23.0,"contact_point_centroid":[0.47757,0.08371,0.04936],"force_p95":110.39212,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":139.80355,"mean_force":67.56878,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47222,0.09372,0.05167]},{"body_a":"attachment","body_b":"push_box","contact_count":338.0,"contact_point_centroid":[0.49121,-0.02787,0.04247],"force_p95":67.5181,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":84.25485,"mean_force":11.94108,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48203,-0.01652,0.0297]},{"body_a":"world","body_b":"push_box","contact_count":1280.0,"contact_point_centroid":[0.47929,0.05909,-3e-05],"force_p95":0.30915,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":70.19321,"mean_force":1.46605,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47396,0.07491,0.08159]},{"body_a":"world","body_b":"push_box","contact_count":542.0,"contact_point_centroid":[0.49439,-0.0544,-0.00012],"force_p95":36.87018,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":54.52967,"mean_force":8.87563,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48117,-0.00675,0.03072]},{"body_a":"push_box","body_b":"link7","contact_count":64.0,"contact_point_centroid":[0.51741,-0.03094,0.05675],"force_p95":40.77041,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.12565,"mean_force":8.59895,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48235,-0.01893,0.02951]},{"body_a":"world","body_b":"push_box","contact_count":1300.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48928,0.02495,0.21273]}],"total_contact_groups":6},"final_pose_error":0.01982,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49931,-0.16783,0.02507],"final_tcp_position":[0.49439,-0.13139,0.02116],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":139.80355,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":325.0,"n_steps_budget":600.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1300.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_standoff","tcp_end":[0.47885,0.05132,0.12325],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.09852,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":328.0,"n_steps_budget":600.0,"object_pos_end":[0.47941,0.05841,0.02489],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.20942,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":0.24483,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1303.0,"raw_peak_contact_force":139.80355,"subtask_id":"reach_contact","tcp_end":[0.47177,0.10046,0.04158],"tcp_start":[0.47885,0.05132,0.12325],"tcp_to_object_dist_end":0.04588,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":501.0,"n_steps_budget":600.0,"object_pos_end":[0.49931,-0.16783,0.02507],"object_pos_start":[0.47941,0.05841,0.02489],"object_to_goal_dist_end":0.01785,"object_to_goal_dist_start":0.20942,"object_z_max":0.03041,"peak_contact_force":1.65579,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":944.0,"raw_peak_contact_force":84.25485,"subtask_id":"push_complete","tcp_end":[0.49439,-0.13139,0.02116],"tcp_start":[0.47177,0.10046,0.04158],"tcp_to_object_dist_end":0.03698,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```