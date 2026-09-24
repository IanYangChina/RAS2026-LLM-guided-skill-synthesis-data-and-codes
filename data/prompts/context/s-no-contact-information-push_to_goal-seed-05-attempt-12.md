## Search State

- **Seed**: 5
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | -0.0272 | 0.25 | ❌ rejected |
| 11 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.6462 | 0.58 | ✅ accepted |
| 10 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.2840 | 0.34 | ❌ rejected |
| 9 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.2725 | 0.38 | ✅ accepted |
| 8 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.0820 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.25 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.027) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: approach_contact
  anchor: object
  weight: 0.4
- id: push_goal
  target_entity: object
  metric: goal_progress
  weight: 0.6
phases:
- id: approach_side
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
    - 0.0
    offset_along_axis:
      distance: 0.04
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: negative
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_contact
- id: contact_side
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.02
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 10.0
      - 30.0
      default: 20.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_established
    when: during_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: continue
  subtask_id: approach_contact
- id: push_to_goal
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
      distance: 0.02
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: negative
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_side** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.04, mode=replace_offset_projection, sign=negative}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **contact_side** (`contact`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.02, mode=replace_offset_projection, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_established, when=during_phase, predicate=contact_detected, on_failure=continue, threshold=1.0
- **push_to_goal** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.02, mode=replace_offset_projection, sign=negative}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.027
- **task_score** (E): 0.248
- **fitness_score**: 0.303  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_behind | 1.00 | 0.2712 |
| contact_side | 0.33 | 0.0508 |
| push_follow | 1.00 | 0.0115 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_behind | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.517, 0.063, 0.039) | (0.519, 0.022, 0.025)→(0.519, 0.021, 0.025) | 0.173→0.173 |
| contact_side | contact | 0.33 / step_budget | (0.517, 0.063, 0.039)→(0.514, 0.016, 0.021) | (0.519, 0.021, 0.025)→(0.524, -0.020, 0.025) | 0.173→0.132 |
| push_follow | push | 1.00 / time_limit | (0.514, 0.016, 0.021)→(0.525, 0.019, 0.020) | (0.524, -0.020, 0.025)→(0.524, -0.021, 0.025) | 0.132→0.132 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.323
- approach_alignment: 0.535
- goal_progress: 0.308
- terminal_score: 0.308
- phase_score: 0.347
- phase_breakdown.push_goal_score: 0.007

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.331
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.308
- **Median Q (composite search score)**: -0.041
- **K-run variance**: 0.0004
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.360


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.51667,"average_solve_count":60.0,"average_success_count":60.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.30753,"approach_behind.arc_height":0.044,"contact_side.contact_force_threshold":20.26996,"contact_side.contact_speed":0.05373,"push_follow.push_duration":2.0152,"push_follow.push_speed":0.14338},"optimized_scores":{"best_composite_score":-0.04067,"best_fitness_score":0.28933,"best_task_score":0.22593},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":8.0,"contact_point_centroid":[0.53537,0.06144,0.04793],"force_p95":56.15905,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":56.47598,"mean_force":47.51297,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.53536,0.07327,0.04792]},{"body_a":"attachment","body_b":"push_box","contact_count":443.0,"contact_point_centroid":[0.53596,0.03836,0.04628],"force_p95":14.80931,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.27286,"mean_force":7.28955,"phase_index":1.0,"phase_name":"contact_side","phase_type":"contact","tcp_position_centroid":[0.53164,0.05024,0.0294]},{"body_a":"world","body_b":"push_box","contact_count":1838.0,"contact_point_centroid":[0.5366,0.0368,-1e-05],"force_p95":0.24532,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.53597,"mean_force":0.45155,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.51589,0.05768,0.17982]},{"body_a":"world","body_b":"push_box","contact_count":911.0,"contact_point_centroid":[0.5377,-0.00037,-6e-05],"force_p95":7.6552,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.1781,"mean_force":3.90887,"phase_index":1.0,"phase_name":"contact_side","phase_type":"contact","tcp_position_centroid":[0.53188,0.05327,0.03075]},{"body_a":"attachment","body_b":"push_box","contact_count":14.0,"contact_point_centroid":[0.53801,0.01778,0.05019],"force_p95":5.25495,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.26661,"mean_force":3.12716,"phase_index":2.0,"phase_name":"push_follow","phase_type":"push","tcp_position_centroid":[0.53054,0.02965,0.0206]},{"body_a":"world","body_b":"push_box","contact_count":1788.0,"contact_point_centroid":[0.53842,-0.00778,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.91124,"mean_force":0.27235,"phase_index":2.0,"phase_name":"push_follow","phase_type":"push","tcp_position_centroid":[0.53543,0.03057,0.01842]}],"total_contact_groups":6},"final_pose_error":0.0089,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5384,-0.00763,0.02499],"final_tcp_position":[0.54216,0.03144,0.0195],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"phases":[{"n_steps":463.0,"n_steps_budget":600.0,"object_pos_end":[0.53666,0.03552,0.02486],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.18911,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_contact","tcp_end":[0.53604,0.0724,0.04269],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.04097,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.53833,-0.00661,0.02543],"object_pos_start":[0.53666,0.03552,0.02486],"object_to_goal_dist_end":0.14843,"object_to_goal_dist_start":0.18911,"object_z_max":0.02548,"phase_name":"contact_side","phase_peak_obstacle_force":0.0,"phase_type":"contact","subtask_id":"approach_contact","tcp_end":[0.53074,0.0298,0.02127],"tcp_start":[0.53604,0.0724,0.04269],"tcp_to_object_dist_end":0.03742,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.5384,-0.00763,0.02499],"object_pos_start":[0.53833,-0.00661,0.02543],"object_to_goal_dist_end":0.14746,"object_to_goal_dist_start":0.14843,"object_z_max":0.02543,"phase_name":"push_follow","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_goal","tcp_end":[0.54216,0.03144,0.0195],"tcp_start":[0.53074,0.0298,0.02127],"tcp_to_object_dist_end":0.03963,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.7,"average_solve_count":60.0,"average_success_count":60.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.31097,"approach_behind.arc_height":0.09365,"contact_side.contact_force_threshold":21.50924,"contact_side.contact_speed":0.06853,"push_follow.push_duration":3.9441,"push_follow.push_speed":0.16866},"optimized_scores":{"best_composite_score":0.00137,"best_fitness_score":0.33137,"best_task_score":0.30811},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":380.0,"contact_point_centroid":[0.50388,-0.01459,0.04288],"force_p95":13.0747,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.27119,"mean_force":5.13309,"phase_index":1.0,"phase_name":"contact_side","phase_type":"contact","tcp_position_centroid":[0.49936,-0.00268,0.02429]},{"body_a":"attachment","body_b":"push_box","contact_count":22.0,"contact_point_centroid":[0.50783,-0.03567,0.05024],"force_p95":7.82993,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.854,"mean_force":3.55611,"phase_index":2.0,"phase_name":"push_follow","phase_type":"push","tcp_position_centroid":[0.50007,-0.02379,0.02037]},{"body_a":"world","body_b":"push_box","contact_count":983.0,"contact_point_centroid":[0.50868,-0.04512,-3e-05],"force_p95":6.76717,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.98182,"mean_force":2.33278,"phase_index":1.0,"phase_name":"contact_side","phase_type":"contact","tcp_position_centroid":[0.49949,0.00751,0.02645]},{"body_a":"world","body_b":"push_box","contact_count":1784.0,"contact_point_centroid":[0.51373,-0.0605,-1e-05],"force_p95":0.24581,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.549,"mean_force":0.29121,"phase_index":2.0,"phase_name":"push_follow","phase_type":"push","tcp_position_centroid":[0.50583,-0.02181,0.01895]},{"body_a":"world","body_b":"push_box","contact_count":2084.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50046,0.06533,0.17269]}],"total_contact_groups":5},"final_pose_error":0.00826,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51368,-0.06021,0.02499],"final_tcp_position":[0.513,-0.02028,0.02016],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"phases":[{"n_steps":521.0,"n_steps_budget":600.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_contact","tcp_end":[0.50194,0.02904,0.03346],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.04866,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":516.0,"n_steps_budget":600.0,"object_pos_end":[0.51336,-0.05952,0.02541],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.09146,"object_to_goal_dist_start":0.13127,"object_z_max":0.02552,"phase_name":"contact_side","phase_peak_obstacle_force":0.0,"phase_type":"contact","subtask_id":"approach_contact","tcp_end":[0.50014,-0.02379,0.0211],"tcp_start":[0.50194,0.02904,0.03346],"tcp_to_object_dist_end":0.03834,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.51368,-0.06021,0.02499],"object_pos_start":[0.51336,-0.05952,0.02541],"object_to_goal_dist_end":0.09083,"object_to_goal_dist_start":0.09146,"object_z_max":0.02542,"phase_name":"push_follow","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_goal","tcp_end":[0.513,-0.02028,0.02016],"tcp_start":[0.50014,-0.02379,0.0211],"tcp_to_object_dist_end":0.04023,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.47692,"average_solve_count":130.0,"average_success_count":130.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.06452,"approach_behind.arc_height":0.06841,"contact_side.contact_force_threshold":25.35624,"contact_side.contact_speed":0.05711,"push_follow.push_duration":4.42218,"push_follow.push_speed":0.15182},"optimized_scores":{"best_composite_score":-0.04239,"best_fitness_score":0.28761,"best_task_score":0.20882},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":415.0,"contact_point_centroid":[0.51444,0.05115,0.04563],"force_p95":15.59807,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.90981,"mean_force":7.08496,"phase_index":1.0,"phase_name":"contact_side","phase_type":"contact","tcp_position_centroid":[0.50963,0.06296,0.02854]},{"body_a":"attachment","body_b":"push_box","contact_count":35.0,"contact_point_centroid":[0.51804,0.03022,0.0504],"force_p95":11.56447,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.44572,"mean_force":5.01824,"phase_index":2.0,"phase_name":"push_follow","phase_type":"push","tcp_position_centroid":[0.50995,0.04202,0.02053]},{"body_a":"world","body_b":"push_box","contact_count":893.0,"contact_point_centroid":[0.51886,0.01394,-5e-05],"force_p95":8.13706,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.53812,"mean_force":3.67385,"phase_index":1.0,"phase_name":"contact_side","phase_type":"contact","tcp_position_centroid":[0.50979,0.06775,0.03045]},{"body_a":"world","body_b":"push_box","contact_count":1644.0,"contact_point_centroid":[0.52056,0.00475,-1e-05],"force_p95":0.38207,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.57464,"mean_force":0.3555,"phase_index":2.0,"phase_name":"push_follow","phase_type":"push","tcp_position_centroid":[0.51395,0.04341,0.01902]},{"body_a":"world","body_b":"push_box","contact_count":2480.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50455,0.07782,0.18573]}],"total_contact_groups":5},"final_pose_error":0.00822,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5205,0.00549,0.02499],"final_tcp_position":[0.51914,0.0447,0.0199],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"phases":[{"n_steps":620.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_contact","tcp_end":[0.51245,0.08813,0.04107],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.04362,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.52004,0.00587,0.02537],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.15716,"object_to_goal_dist_start":0.19823,"object_z_max":0.02567,"phase_name":"contact_side","phase_peak_obstacle_force":0.0,"phase_type":"contact","subtask_id":"approach_contact","tcp_end":[0.51012,0.04191,0.02159],"tcp_start":[0.51245,0.08813,0.04107],"tcp_to_object_dist_end":0.03757,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":426.0,"n_steps_budget":600.0,"object_pos_end":[0.5205,0.00549,0.02499],"object_pos_start":[0.52004,0.00587,0.02537],"object_to_goal_dist_end":0.15684,"object_to_goal_dist_start":0.15716,"object_z_max":0.02538,"phase_name":"push_follow","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_goal","tcp_end":[0.51914,0.0447,0.0199],"tcp_start":[0.51012,0.04191,0.02159],"tcp_to_object_dist_end":0.03956,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```