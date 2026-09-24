## Search State

- **Seed**: 5
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → push | arc_cartesian | linear_cartesian | position_control | force_threshold_switch | pose_tolerance | force_exceeded | 7 | 0.3215 | 0.32 | ❌ rejected |
| 9 | approach → push | arc_cartesian | linear_cartesian | position_control | impedance_control | time_limit | pose_tolerance | 6 | 0.5135 | 0.88 | ❌ rejected |
| 8 | approach → push | arc_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 8 | 0.4132 | 0.91 | ❌ rejected |
| 7 | approach → push | arc_cartesian | linear_cartesian | position_control | impedance_control | time_limit | time_limit | 8 | 0.4231 | 0.90 | ❌ rejected |
| 6 | approach → push | arc_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 8 | 0.4204 | 0.91 | ❌ rejected |

**Proposal policy**: task_score is 0.32 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.922, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.5366003508494456, 0.03695289476837925, 0.025) | approach/contact targets near object start |
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

## Current Skill (Q=0.321) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: pre_contact
  anchor: object
  weight: 0.3
- id: push_to_goal
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.005
    offset_along_axis:
      distance: 0.02
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: negative
    orientation:
      mode: none
  parameters:
    approach_arc_height:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.arc_height
        mode: replace
    approach_behind:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    approach_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    approach_z:
      type: scalar
      range:
      - 0.0
      - 0.02
      default: 0.005
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: pre_contact
- id: push_1
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
      distance: 0.35
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: positive
    orientation:
      mode: none
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.2
      - 0.5
      default: 0.35
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    push_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  guards:
  - id: contact_check
    when: during_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.005
    - 0.0
  subtask_id: push_to_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.005], offset_along_axis={axis=task_goal_direction, distance=0.02, mode=replace_offset_projection, sign=negative}
  - orientation: mode=none
  - parameter_bindings:
    - approach_arc_height: status=consumed; consumers=generator.arc_height (replace)
    - approach_behind: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
    - approach_z: status=consumed; consumers=target.offset.z (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.35, mode=replace_offset_projection, sign=positive}
  - orientation: mode=none
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=contact_check, when=during_phase, predicate=contact_detected, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.005, 0.0]

## Design Metrics

- **Composite score**: 0.321
- **task_score** (E): 0.317
- **fitness_score**: 0.338  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.350

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2724 |
| push_1 | 1.00 | 1.00 | 0.0524 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, 0.058, 0.037) | (0.519, 0.022, 0.025)→(0.519, 0.020, 0.025) | 0.173→0.171 | 1.00 / 3.667 | 22.129 | 23.399 |
| push_1 | push | 1.00 / force_exceeded | (0.516, 0.058, 0.037)→(0.512, 0.006, 0.031) | (0.519, 0.020, 0.025)→(0.522, -0.029, 0.027) | 0.171→0.123 | 1.00 / 3.333 | 1.418 | 20.652 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.349
- lateral_force_integral: None
- approach_alignment: 0.477
- goal_progress: 0.341
- terminal_score: 0.341
- phase_score: 0.372
- phase_breakdown.push_to_goal_score: 0.341
- phase_breakdown.pre_contact_score: 0.443

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.546
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.566
- **Median Q (composite search score)**: 0.259
- **K-run variance**: 0.0183
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.296


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93103,"average_solve_count":87.0,"average_success_count":87.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_arc_height":0.11599,"approach_1.approach_behind":0.01759,"approach_1.approach_speed":0.06456,"approach_1.approach_tolerance":0.0148,"approach_1.approach_z":0.01662,"push_1.push_force_threshold":21.08472,"push_1.push_speed":0.11256},"optimized_scores":{"best_composite_score":0.25872,"best_fitness_score":0.10872,"best_task_score":0.04322},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":16.0,"contact_point_centroid":[0.53538,0.06006,0.04734],"force_p95":56.71764,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":61.46622,"mean_force":18.53242,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.53457,0.07168,0.04525]},{"body_a":"world","body_b":"push_box","contact_count":3873.0,"contact_point_centroid":[0.5366,0.0369,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.86095,"mean_force":0.32106,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51305,0.09681,0.19414]},{"body_a":"attachment","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.53691,0.05327,0.04989],"force_p95":22.6841,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.9677,"mean_force":20.05198,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53354,0.06511,0.04154]},{"body_a":"world","body_b":"push_box","contact_count":41.0,"contact_point_centroid":[0.5372,0.01235,-5e-05],"force_p95":11.54051,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.9952,"mean_force":2.45341,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53409,0.06608,0.04213]}],"total_contact_groups":4},"final_pose_error":0.21793,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53755,0.02836,0.02488],"final_tcp_position":[0.53334,0.06475,0.04132],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":61.46622,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":982.0,"n_steps_budget":1000.0,"object_pos_end":[0.53738,0.03003,0.02521],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.18387,"object_to_goal_dist_start":0.1905,"object_z_max":0.02534,"peak_contact_force":22.9677,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":45.0,"raw_peak_contact_force":22.9677,"subtask_id":"pre_contact","tcp_end":[0.53495,0.06785,0.04322],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.04196,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":17.0,"n_steps_budget":1000.0,"object_pos_end":[0.53755,0.02836,0.02488],"object_pos_start":[0.53738,0.03003,0.02521],"object_to_goal_dist_end":0.18227,"object_to_goal_dist_start":0.18387,"object_z_max":0.02521,"peak_contact_force":3.76317,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3889.0,"raw_peak_contact_force":61.46622,"subtask_id":"push_to_goal","tcp_end":[0.53334,0.06475,0.04132],"tcp_start":[0.53495,0.06785,0.04322],"tcp_to_object_dist_end":0.04016,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.64706,"average_solve_count":119.0,"average_success_count":119.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_arc_height":0.07863,"approach_1.approach_behind":0.02497,"approach_1.approach_speed":0.06816,"approach_1.approach_tolerance":0.01522,"approach_1.approach_z":0.00207,"push_1.push_force_threshold":24.83056,"push_1.push_speed":0.04687},"optimized_scores":{"best_composite_score":0.19617,"best_fitness_score":0.54617,"best_task_score":0.56572},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1469.0,"contact_point_centroid":[0.51143,-0.07286,-6e-05],"force_p95":12.7791,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.95621,"mean_force":3.94852,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49717,-0.01667,0.02671]},{"body_a":"attachment","body_b":"push_box","contact_count":923.0,"contact_point_centroid":[0.50745,-0.03241,0.04458],"force_p95":11.61038,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.49377,"mean_force":4.53503,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49698,-0.02064,0.02633]},{"body_a":"push_box","body_b":"link7","contact_count":210.0,"contact_point_centroid":[0.53147,-0.06397,0.05296],"force_p95":12.42426,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.70616,"mean_force":5.7398,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49677,-0.04711,0.02505]},{"body_a":"world","body_b":"push_box","contact_count":3136.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49977,0.05394,0.17052]}],"total_contact_groups":4},"final_pose_error":0.09196,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5089,-0.09375,0.0276],"final_tcp_position":[0.49703,-0.05809,0.02485],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":22.95621,"phases":[{"contact_detected":true,"contact_event_count":3.0,"n_steps":784.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":19.14649,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2602.0,"raw_peak_contact_force":22.95621,"subtask_id":"pre_contact","tcp_end":[0.5012,0.01942,0.03271],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.03914,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5089,-0.09375,0.0276],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.05701,"object_to_goal_dist_start":0.13127,"object_z_max":0.02759,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3136.0,"raw_peak_contact_force":0.24534,"subtask_id":"push_to_goal","tcp_end":[0.49703,-0.05809,0.02485],"tcp_start":[0.5012,0.01942,0.03271],"tcp_to_object_dist_end":0.03769,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.49206,"average_solve_count":63.0,"average_success_count":63.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_arc_height":0.14317,"approach_1.approach_behind":0.01481,"approach_1.approach_speed":0.15104,"approach_1.approach_tolerance":0.02642,"approach_1.approach_z":0.00199,"push_1.push_force_threshold":21.7334,"push_1.push_speed":0.07382},"optimized_scores":{"best_composite_score":0.5096,"best_fitness_score":0.3596,"best_task_score":0.34129},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":910.0,"contact_point_centroid":[0.522,-0.00295,-5e-05],"force_p95":10.39701,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.27411,"mean_force":4.2929,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5064,0.05121,0.02895]},{"body_a":"attachment","body_b":"push_box","contact_count":524.0,"contact_point_centroid":[0.51558,0.03709,0.0451],"force_p95":15.21253,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.40802,"mean_force":5.54667,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50602,0.04863,0.02856]},{"body_a":"push_box","body_b":"link7","contact_count":68.0,"contact_point_centroid":[0.54114,0.0037,0.05462],"force_p95":15.91467,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.35831,"mean_force":10.04598,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50437,0.01744,0.02722]},{"body_a":"world","body_b":"push_box","contact_count":2376.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50414,0.11342,0.19376]}],"total_contact_groups":4},"final_pose_error":0.16253,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52094,-0.02116,0.02853],"final_tcp_position":[0.5044,0.01246,0.02729],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":24.27411,"phases":[{"contact_detected":true,"contact_event_count":3.0,"n_steps":594.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":24.27411,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1502.0,"raw_peak_contact_force":24.27411,"subtask_id":"pre_contact","tcp_end":[0.51177,0.08707,0.03469],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.04071,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":613.0,"n_steps_budget":1000.0,"object_pos_end":[0.52094,-0.02116,0.02853],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.13058,"object_to_goal_dist_start":0.19823,"object_z_max":0.02851,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2376.0,"raw_peak_contact_force":0.24534,"subtask_id":"push_to_goal","tcp_end":[0.5044,0.01246,0.02729],"tcp_start":[0.51177,0.08707,0.03469],"tcp_to_object_dist_end":0.03749,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```