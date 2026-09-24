## Search State

- **Seed**: 5
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.0808 | 0.00 | ✅ accepted |
| 6 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 2 | -0.0093 | 0.00 | ❌ rejected |
| 5 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.0610 | 0.00 | ❌ rejected |
| 4 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.2924 | 0.00 | ❌ rejected |
| 3 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 2 | -0.0093 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.00 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.081) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: approach_contact
  anchor: object
  offset:
  - 0.025
  - 0.025
  - 0.0
  weight: 0.4
- id: push_goal
  target_entity: object
  metric: goal_progress
  weight: 0.6
phases:
- id: approach_high
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.025
    - 0.025
    - 0.08
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_high_speed:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_contact
- id: descend_to_contact
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.025
    - 0.025
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 5.0
      - 30.0
      default: 15.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_contact
- id: push_to_goal
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.025
    - 0.025
    - 0.0
    offset_along_axis:
      distance: 0.25
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
      - 0.15
      - 0.35
      default: 0.25
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_limit
    when: during_phase
    predicate: force_below
    threshold: 25.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: reduce_speed
  subtask_id: push_goal
- id: lift_after_push
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
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_high** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.025, 0.025, 0.08], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_high_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_contact** (`contact`)
  - target: source=yaml, anchor=task_object, offset=[0.025, 0.025, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **push_to_goal** (`push`)
  - target: source=yaml, anchor=task_object, offset=[0.025, 0.025, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.25, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_limit, when=during_phase, predicate=force_below, on_failure=retry, threshold=25.0
  - retries: max_attempts=2, strategy=reduce_speed
- **lift_after_push** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.081
- **task_score** (E): 0.003
- **fitness_score**: 0.141  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_high | 1.00 | 0.1994 |
| descend_to_contact | 1.00 | 0.0609 |
| push_to_goal | 0.00 | 0.0001 |
| lift_after_push | 1.00 | 0.0880 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_high | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.538, 0.044, 0.112) | (0.519, 0.022, 0.025)→(0.519, 0.022, 0.025) | 0.173→0.173 |
| descend_to_contact | contact | 1.00 / force_exceeded | (0.538, 0.044, 0.112)→(0.537, 0.045, 0.051) | (0.519, 0.022, 0.025)→(0.519, 0.022, 0.025) | 0.173→0.173 |
| push_to_goal | push | 0.00 / guard_failure | (0.537, 0.045, 0.051)→(0.537, 0.045, 0.051) | (0.519, 0.022, 0.025)→(0.519, 0.022, 0.025) | 0.173→0.173 |
| lift_after_push | retract | 1.00 / step_budget | (0.537, 0.045, 0.051)→(0.534, 0.045, 0.139) | (0.519, 0.022, 0.025)→(0.517, 0.022, 0.025) | 0.173→0.173 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.008
- approach_alignment: 0.480
- goal_progress: 0.001
- terminal_score: 0.001
- phase_score: 0.234
- phase_breakdown.push_goal_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.141
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.004
- **Median Q (composite search score)**: 0.081
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.262


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.33621,"average_solve_count":116.0,"average_success_count":116.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.approach_high_speed":0.06829,"descend_to_contact.contact_force_threshold":23.85049,"descend_to_contact.descend_speed":0.04732,"push_to_goal.push_distance":0.21861,"push_to_goal.push_speed":0.09321},"optimized_scores":{"best_composite_score":0.08049,"best_fitness_score":0.14049,"best_task_score":0.00357},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.56148,0.06196,0.04989],"force_p95":52.34295,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":55.56438,"mean_force":26.5786,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.55469,0.05993,0.05124]},{"body_a":"attachment","body_b":"push_box","contact_count":11.0,"contact_point_centroid":[0.56059,0.05665,0.04995],"force_p95":36.36311,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.84532,"mean_force":12.42055,"phase_index":3.0,"phase_name":"lift_after_push","phase_type":"retract","tcp_position_centroid":[0.55416,0.05988,0.05112]},{"body_a":"world","body_b":"push_box","contact_count":7.0,"contact_point_centroid":[0.53298,0.04049,-1e-05],"force_p95":28.40605,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.64558,"mean_force":11.51264,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.55469,0.05993,0.05125]},{"body_a":"world","body_b":"push_box","contact_count":2152.0,"contact_point_centroid":[0.53448,0.03668,-1e-05],"force_p95":0.24543,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.34672,"mean_force":0.3116,"phase_index":3.0,"phase_name":"lift_after_push","phase_type":"retract","tcp_position_centroid":[0.55107,0.05949,0.09402]},{"body_a":"world","body_b":"push_box","contact_count":2992.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.52613,0.02872,0.20438]},{"body_a":"world","body_b":"push_box","contact_count":1380.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"contact","tcp_position_centroid":[0.55328,0.0588,0.07903]}],"total_contact_groups":6},"final_pose_error":0.01294,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53462,0.03664,0.02499],"final_tcp_position":[0.55121,0.0595,0.13856],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"phases":[{"n_steps":748.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_contact","tcp_end":[0.55449,0.05795,0.11051],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08986,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":345.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.02499,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","subtask_id":"approach_contact","tcp_end":[0.55472,0.05992,0.05134],"tcp_start":[0.55449,0.05795,0.11051],"tcp_to_object_dist_end":0.03938,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.53654,0.03694,0.02502],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.19048,"object_to_goal_dist_start":0.1905,"object_z_max":0.02502,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_goal","tcp_end":[0.55459,0.05993,0.05104],"tcp_start":[0.55464,0.05993,0.05113],"tcp_to_object_dist_end":0.03913,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":546.0,"n_steps_budget":630.0,"object_pos_end":[0.53462,0.03664,0.02499],"object_pos_start":[0.5364,0.0369,0.02496],"object_to_goal_dist_end":0.18982,"object_to_goal_dist_start":0.19041,"object_z_max":0.02518,"phase_name":"lift_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.55121,0.0595,0.13856],"tcp_start":[0.55459,0.05993,0.05104],"tcp_to_object_dist_end":0.11703,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.01639,"average_solve_count":61.0,"average_success_count":61.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.approach_high_speed":0.3112,"descend_to_contact.contact_force_threshold":18.77682,"descend_to_contact.descend_speed":0.08655,"push_to_goal.push_distance":0.2639,"push_to_goal.push_speed":0.10243},"optimized_scores":{"best_composite_score":0.08102,"best_fitness_score":0.14102,"best_task_score":0.00108},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.52946,0.0062,0.04989],"force_p95":55.8487,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":58.94836,"mean_force":29.32078,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.52369,0.00588,0.05098]},{"body_a":"world","body_b":"push_box","contact_count":6.0,"contact_point_centroid":[0.49623,-0.01882,-1e-05],"force_p95":35.85012,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":38.43889,"mean_force":14.78819,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.52371,0.00588,0.05104]},{"body_a":"attachment","body_b":"push_box","contact_count":13.0,"contact_point_centroid":[0.52856,-0.00451,0.04996],"force_p95":27.76068,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.79716,"mean_force":8.44956,"phase_index":3.0,"phase_name":"lift_after_push","phase_type":"retract","tcp_position_centroid":[0.52302,0.00585,0.05094]},{"body_a":"world","body_b":"push_box","contact_count":2142.0,"contact_point_centroid":[0.50332,-0.01875,-1e-05],"force_p95":0.24559,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.9097,"mean_force":0.30136,"phase_index":3.0,"phase_name":"lift_after_push","phase_type":"retract","tcp_position_centroid":[0.52019,0.00578,0.09459]},{"body_a":"world","body_b":"push_box","contact_count":2096.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.51117,0.00279,0.20652]},{"body_a":"world","body_b":"push_box","contact_count":1292.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"contact","tcp_position_centroid":[0.52264,0.00573,0.08088]}],"total_contact_groups":6},"final_pose_error":0.01226,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5035,-0.01892,0.02499],"final_tcp_position":[0.52031,0.00579,0.13897],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"phases":[{"n_steps":524.0,"n_steps_budget":600.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_contact","tcp_end":[0.52416,0.00566,0.11329],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0937,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":323.0,"n_steps_budget":660.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","subtask_id":"approach_contact","tcp_end":[0.52372,0.00588,0.05109],"tcp_start":[0.52416,0.00566,0.11329],"tcp_to_object_dist_end":0.04071,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50453,-0.01881,0.02502],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02502,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_goal","tcp_end":[0.52358,0.00588,0.05078],"tcp_start":[0.52364,0.00588,0.05088],"tcp_to_object_dist_end":0.04046,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":547.0,"n_steps_budget":630.0,"object_pos_end":[0.5035,-0.01892,0.02499],"object_pos_start":[0.50439,-0.01881,0.02499],"object_to_goal_dist_end":0.13113,"object_to_goal_dist_start":0.13126,"object_z_max":0.02524,"phase_name":"lift_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.52031,0.00579,0.13897],"tcp_start":[0.52358,0.00588,0.05078],"tcp_to_object_dist_end":0.11783,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.53488,"average_solve_count":86.0,"average_success_count":86.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.approach_high_speed":0.27832,"descend_to_contact.contact_force_threshold":15.96739,"descend_to_contact.descend_speed":0.03226,"push_to_goal.push_distance":0.24147,"push_to_goal.push_speed":0.09704},"optimized_scores":{"best_composite_score":0.08085,"best_fitness_score":0.14085,"best_task_score":0.0035},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.53992,0.07267,0.04994],"force_p95":47.85101,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":51.72187,"mean_force":21.62809,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.53368,0.07016,0.05122]},{"body_a":"world","body_b":"push_box","contact_count":6.0,"contact_point_centroid":[0.50665,0.04765,-1e-05],"force_p95":28.09425,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.31874,"mean_force":11.02605,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.5337,0.07016,0.05125]},{"body_a":"attachment","body_b":"push_box","contact_count":8.0,"contact_point_centroid":[0.53929,0.07264,0.04991],"force_p95":30.97193,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.82057,"mean_force":11.96603,"phase_index":3.0,"phase_name":"lift_after_push","phase_type":"retract","tcp_position_centroid":[0.53325,0.0701,0.05106]},{"body_a":"world","body_b":"push_box","contact_count":2266.0,"contact_point_centroid":[0.51338,0.04712,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.06752,"mean_force":0.28977,"phase_index":3.0,"phase_name":"lift_after_push","phase_type":"retract","tcp_position_centroid":[0.53015,0.06965,0.09455]},{"body_a":"world","body_b":"push_box","contact_count":2192.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.51585,0.03289,0.20687]},{"body_a":"world","body_b":"push_box","contact_count":1460.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"contact","tcp_position_centroid":[0.53245,0.06859,0.08023]}],"total_contact_groups":6},"final_pose_error":0.01224,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51337,0.04709,0.02499],"final_tcp_position":[0.53028,0.06968,0.13928],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"phases":[{"n_steps":548.0,"n_steps_budget":600.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_contact","tcp_end":[0.53386,0.06736,0.11241],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.09158,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":365.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","subtask_id":"approach_contact","tcp_end":[0.53373,0.07016,0.0513],"tcp_start":[0.53386,0.06736,0.11241],"tcp_to_object_dist_end":0.03935,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.51496,0.04765,0.02502],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19822,"object_to_goal_dist_start":0.19823,"object_z_max":0.02502,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_goal","tcp_end":[0.53358,0.07015,0.05105],"tcp_start":[0.53363,0.07015,0.05114],"tcp_to_object_dist_end":0.03912,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.51337,0.04709,0.02499],"object_pos_start":[0.51484,0.04762,0.025],"object_to_goal_dist_end":0.19754,"object_to_goal_dist_start":0.19818,"object_z_max":0.02508,"phase_name":"lift_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.53028,0.06968,0.13928],"tcp_start":[0.53358,0.07015,0.05105],"tcp_to_object_dist_end":0.11772,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```