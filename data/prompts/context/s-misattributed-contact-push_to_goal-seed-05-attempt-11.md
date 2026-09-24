## Search State

- **Seed**: 5
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → push | arc_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | force_exceeded | 8 | -0.1053 | 0.04 | ❌ rejected |
| 10 | approach → push | arc_cartesian | linear_cartesian | position_control | force_threshold_switch | pose_tolerance | force_exceeded | 7 | 0.3215 | 0.32 | ❌ rejected |
| 9 | approach → push | arc_cartesian | linear_cartesian | position_control | impedance_control | time_limit | pose_tolerance | 6 | 0.5135 | 0.88 | ❌ rejected |
| 8 | approach → push | arc_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 8 | 0.4132 | 0.91 | ❌ rejected |
| 7 | approach → push | arc_cartesian | linear_cartesian | position_control | impedance_control | time_limit | time_limit | 8 | 0.4231 | 0.90 | ❌ rejected |

**Proposal policy**: task_score is 0.04 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.105) — your mutation base

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

- **Composite score**: -0.105
- **task_score** (E): 0.040
- **fitness_score**: 0.128  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.400

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2588 |
| push_1 | 0.33 | 1.00 | 0.0014 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.521, 0.040, 0.047) | (0.519, 0.022, 0.025)→(0.520, 0.021, 0.025) | 0.173→0.172 | 1.00 / 4.000 | 99.819 | 74.695 |
| push_1 | push | 0.33 / guard_failure | (0.521, 0.040, 0.047)→(0.520, 0.039, 0.046) | (0.520, 0.021, 0.025)→(0.518, 0.017, 0.024) | 0.172→0.169 | 1.00 / 3.000 | 174.728 | 278.948 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.127
- lateral_force_integral: None
- approach_alignment: 0.479
- goal_progress: 0.121
- terminal_score: 0.121
- phase_score: 0.203
- phase_breakdown.push_to_goal_score: 0.085
- phase_breakdown.pre_contact_score: 0.479

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.170
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.121
- **Median Q (composite search score)**: -0.292
- **K-run variance**: 0.0706
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.341


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.93496,"average_solve_count":123.0,"average_success_count":123.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_arc_height":0.01139,"approach_1.approach_behind":0.01324,"approach_1.approach_speed":0.02637,"approach_1.approach_tolerance":0.02267,"approach_1.approach_z":0.00131,"push_1.push_distance":0.49542,"push_1.push_force_threshold":21.28175,"push_1.push_speed":0.08378},"optimized_scores":{"best_composite_score":-0.29399,"best_fitness_score":0.10601,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":18.0,"contact_point_centroid":[0.54403,0.04819,0.04802],"force_p95":280.89911,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":283.40495,"mean_force":233.50912,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.53277,0.04847,0.0508]},{"body_a":"world","body_b":"push_box","contact_count":1966.0,"contact_point_centroid":[0.53679,0.03713,-1e-05],"force_p95":0.24533,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":188.20376,"mean_force":2.39647,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51482,0.02934,0.17651]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.54668,0.04841,0.04653],"force_p95":108.65835,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":110.8929,"mean_force":92.18201,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53538,0.04903,0.04846]},{"body_a":"world","body_b":"push_box","contact_count":9.0,"contact_point_centroid":[0.54573,0.04528,-0.00061],"force_p95":74.7946,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":87.55781,"mean_force":31.19601,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53538,0.04903,0.04846]}],"total_contact_groups":4},"final_pose_error":0.69788,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53802,0.03739,0.02411],"final_tcp_position":[0.53551,0.04904,0.04839],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":283.40495,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":495.0,"n_steps_budget":1000.0,"object_pos_end":[0.53807,0.0374,0.02417],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.19123,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":88.54741,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12.0,"raw_peak_contact_force":110.8929,"subtask_id":"pre_contact","tcp_end":[0.53528,0.04901,0.04853],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.02713,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.53807,0.03741,0.02414],"object_pos_start":[0.53807,0.0374,0.02417],"object_to_goal_dist_end":0.19124,"object_to_goal_dist_start":0.19123,"object_z_max":0.02417,"peak_contact_force":280.45691,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1984.0,"raw_peak_contact_force":283.40495,"subtask_id":"push_to_goal","tcp_end":[0.53551,0.04904,0.04839],"tcp_start":[0.53546,0.04904,0.0484],"tcp_to_object_dist_end":0.02702,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.9,"average_solve_count":60.0,"average_success_count":60.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_arc_height":0.03031,"approach_1.approach_behind":0.02123,"approach_1.approach_speed":0.09881,"approach_1.approach_tolerance":0.01764,"approach_1.approach_z":0.00333,"push_1.push_distance":0.47085,"push_1.push_force_threshold":20.68115,"push_1.push_speed":0.11622},"optimized_scores":{"best_composite_score":0.27036,"best_fitness_score":0.17036,"best_task_score":0.12091},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":54.0,"contact_point_centroid":[0.51188,0.00494,0.04679],"force_p95":282.6709,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":285.15951,"mean_force":206.67058,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50512,0.01287,0.04838]},{"body_a":"world","body_b":"push_box","contact_count":2323.0,"contact_point_centroid":[0.50496,-0.01859,-4e-05],"force_p95":44.9954,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":188.60971,"mean_force":5.08649,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50022,0.02102,0.16932]},{"body_a":"world","body_b":"push_box","contact_count":24.0,"contact_point_centroid":[0.49754,-0.01166,-0.00024],"force_p95":0.70974,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.82412,"mean_force":0.41933,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50679,0.01146,0.04164]}],"total_contact_groups":3},"final_pose_error":0.63179,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49941,-0.0346,0.02469],"final_tcp_position":[0.50629,0.01056,0.04106],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":285.15951,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":592.0,"n_steps_budget":1000.0,"object_pos_end":[0.5043,-0.0239,0.02567],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.12617,"object_to_goal_dist_start":0.13127,"object_z_max":0.02536,"peak_contact_force":98.54356,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24.0,"raw_peak_contact_force":0.82412,"subtask_id":"pre_contact","tcp_end":[0.50842,0.0128,0.04355],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.04103,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":23.0,"n_steps_budget":1000.0,"object_pos_end":[0.49941,-0.0346,0.02469],"object_pos_start":[0.5043,-0.0239,0.02567],"object_to_goal_dist_end":0.1154,"object_to_goal_dist_start":0.12617,"object_z_max":0.027,"peak_contact_force":0.25903,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2377.0,"raw_peak_contact_force":285.15951,"subtask_id":"push_to_goal","tcp_end":[0.50629,0.01056,0.04106],"tcp_start":[0.50842,0.0128,0.04355],"tcp_to_object_dist_end":0.04852,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.82895,"average_solve_count":76.0,"average_success_count":76.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_arc_height":0.01511,"approach_1.approach_behind":0.01012,"approach_1.approach_speed":0.07653,"approach_1.approach_tolerance":0.01398,"approach_1.approach_z":0.00871,"push_1.push_distance":0.40682,"push_1.push_force_threshold":16.23981,"push_1.push_speed":0.16652},"optimized_scores":{"best_composite_score":-0.2924,"best_fitness_score":0.1076,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":46.0,"contact_point_centroid":[0.52496,0.05718,0.04747],"force_p95":243.85767,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":268.27836,"mean_force":210.77662,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51388,0.05742,0.05058]},{"body_a":"world","body_b":"push_box","contact_count":2792.0,"contact_point_centroid":[0.51537,0.04799,-3e-05],"force_p95":5.99671,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":175.24595,"mean_force":3.73543,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50471,0.03662,0.17343]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.52926,0.05761,0.04605],"force_p95":111.5492,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":112.36742,"mean_force":105.01793,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5181,0.05819,0.04832]},{"body_a":"world","body_b":"push_box","contact_count":9.0,"contact_point_centroid":[0.52476,0.05604,-0.00075],"force_p95":70.50064,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":79.24957,"mean_force":35.44949,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5181,0.05819,0.04832]}],"total_contact_groups":4},"final_pose_error":0.61617,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51719,0.04825,0.02395],"final_tcp_position":[0.51827,0.05818,0.04839],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":268.27836,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":707.0,"n_steps_budget":1000.0,"object_pos_end":[0.5173,0.0483,0.02394],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19906,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":112.36742,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12.0,"raw_peak_contact_force":112.36742,"subtask_id":"pre_contact","tcp_end":[0.518,0.05818,0.04831],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0263,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.51727,0.04829,0.02394],"object_pos_start":[0.5173,0.0483,0.02394],"object_to_goal_dist_end":0.19904,"object_to_goal_dist_start":0.19906,"object_z_max":0.02394,"peak_contact_force":243.46927,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2838.0,"raw_peak_contact_force":268.27836,"subtask_id":"push_to_goal","tcp_end":[0.51827,0.05818,0.04839],"tcp_start":[0.5182,0.05819,0.04834],"tcp_to_object_dist_end":0.02639,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```