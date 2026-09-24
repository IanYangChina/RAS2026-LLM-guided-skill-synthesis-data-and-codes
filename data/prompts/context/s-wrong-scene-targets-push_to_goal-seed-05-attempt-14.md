## Search State

- **Seed**: 5
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → push | arc_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 6 | 0.0279 | 0.38 | ❌ rejected |
| 13 | approach → push | arc_cartesian | linear_cartesian | position_control | impedance_control | time_limit | pose_tolerance | 4 | -0.1037 | 0.05 | ❌ rejected |
| 12 | approach → push | arc_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | time_limit | 4 | 0.5242 | 0.80 | ❌ rejected |
| 11 | approach → push | arc_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | time_limit | 4 | 0.5201 | 0.79 | ❌ rejected |
| 10 | approach → push | arc_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | time_limit | 4 | 0.5328 | 0.81 | ❌ rejected |

**Proposal policy**: task_score is 0.38 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen object start: [0.5, -0.15, 0.025]
- Frozen task target: [0.5, 0.0, 0.3]
- Goal object position: (0.5, 0.0, 0.3)
- Object initial pose: (0.5, -0.15, 0.025)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.8
- Force limit: 25.0 N
- Robot initial TCP position: (0.5366003508494456, 0.03695289476837925, 0.025)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **object displacement ratio toward goal_object_position**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5366003508494456, 0.03695289476837925, 0.025]
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
  frozen_task_target: [0.5, 0.0, 0.3]
  frozen_object_starts: {'push_box': [0.5, -0.15, 0.025]}
  frozen_targets: {'task_goal': [0.5, 0.0, 0.3]}
  push_direction: [-0.0366, -0.187, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.816, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.5, -0.15, 0.025) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, 0.0, 0.3) | final destination targets |
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

## Current Skill (Q=0.028) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: approach_pre_contact
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.025
  weight: 0.3
- id: push_toward_goal
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: arc_behind
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
    - 0.0
    offset_along_axis:
      distance: 0.04
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: negative
    tolerance: 0.01
    orientation:
      mode: none
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    arc_height:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.arc_height
        mode: replace
  subtask_id: approach_pre_contact
- id: push_forward
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.2
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    orientation:
      mode: none
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.05
      - 0.4
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push_toward_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **arc_behind** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.04, mode=replace_offset_projection, sign=negative}, tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
- **push_forward** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.2, mode=add_to_offset, sign=positive}
  - orientation: mode=none
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.028
- **task_score** (E): 0.384
- **fitness_score**: 0.328  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.300

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| arc_behind | 0.67 | 1.00 | 0.2729 |
| push_forward | 1.00 | 1.00 | 0.0671 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| arc_behind | approach | 0.67 / step_budget | (0.500, -0.000, 0.301)→(0.514, -0.001, 0.032) | (0.519, 0.022, 0.025)→(0.528, -0.029, 0.026) | 0.173→0.126 | 1.00 / 3.667 | 97.685 | 167.184 |
| push_forward | push | 1.00 / step_budget | (0.514, -0.001, 0.032)→(0.537, 0.041, 0.032) | (0.528, -0.029, 0.026)→(0.535, -0.039, 0.028) | 0.126→0.121 | 1.00 / 3.333 | 42.689 | 107.404 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.772
- lateral_force_integral: None
- approach_alignment: 0.408
- goal_progress: 0.745
- terminal_score: 0.745
- phase_score: 0.413
- phase_breakdown.push_toward_goal_score: 0.408
- phase_breakdown.approach_pre_contact_score: 0.425

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.546
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.745
- **Median Q (composite search score)**: -0.024
- **K-run variance**: 0.0259
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.281


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
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.5366,0.03695,0.025]}],"axes":[{"name":"push_direction","value":[-0.0366,-0.18695,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5366,0.03695,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.17857,"average_solve_count":56.0,"average_success_count":56.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"arc_behind.approach_speed":0.16314,"arc_behind.approach_tolerance":0.01116,"arc_behind.arc_height":0.13756,"push_forward.push_distance":0.11656,"push_forward.push_speed":0.07652,"push_forward.push_tolerance":0.02968},"optimized_scores":{"best_composite_score":-0.02391,"best_fitness_score":0.27609,"best_task_score":0.40767},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":92.0,"contact_point_centroid":[0.5303,0.02796,0.0499],"force_p95":129.15499,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":143.33283,"mean_force":46.06646,"phase_index":0.0,"phase_name":"arc_behind","phase_type":"approach","tcp_position_centroid":[0.52071,0.03901,0.03403]},{"body_a":"world","body_b":"push_box","contact_count":311.0,"contact_point_centroid":[0.57977,-0.03615,-0.00018],"force_p95":71.14984,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":97.24403,"mean_force":36.66137,"phase_index":1.0,"phase_name":"push_forward","phase_type":"push","tcp_position_centroid":[0.53101,-0.01399,0.02234]},{"body_a":"push_box","body_b":"link7","contact_count":169.0,"contact_point_centroid":[0.57478,-0.02218,0.04935],"force_p95":60.41128,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":90.12922,"mean_force":50.95483,"phase_index":1.0,"phase_name":"push_forward","phase_type":"push","tcp_position_centroid":[0.53247,-0.01623,0.02217]},{"body_a":"world","body_b":"push_box","contact_count":3256.0,"contact_point_centroid":[0.53779,0.03191,-2e-05],"force_p95":15.72904,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":69.11663,"mean_force":2.24498,"phase_index":0.0,"phase_name":"arc_behind","phase_type":"approach","tcp_position_centroid":[0.50843,0.08063,0.1753]},{"body_a":"push_box","body_b":"link7","contact_count":57.0,"contact_point_centroid":[0.56513,0.0025,0.04965],"force_p95":61.23743,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":62.15811,"mean_force":39.33878,"phase_index":0.0,"phase_name":"arc_behind","phase_type":"approach","tcp_position_centroid":[0.52225,0.00805,0.02379]},{"body_a":"attachment","body_b":"push_box","contact_count":161.0,"contact_point_centroid":[0.5521,-0.02546,0.05048],"force_p95":35.69204,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":58.87485,"mean_force":22.25753,"phase_index":1.0,"phase_name":"push_forward","phase_type":"push","tcp_position_centroid":[0.53292,-0.01687,0.02212]}],"total_contact_groups":6},"final_pose_error":0.01492,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.57255,-0.06357,0.02526],"final_tcp_position":[0.54145,-0.03183,0.02122],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":143.33283,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":929.0,"n_steps_budget":1000.0,"object_pos_end":[0.55344,-0.03495,0.02413],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.12686,"object_to_goal_dist_start":0.1905,"object_z_max":0.02628,"peak_contact_force":62.04985,"phase_name":"arc_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3405.0,"raw_peak_contact_force":143.33283,"subtask_id":"approach_pre_contact","tcp_end":[0.52317,-0.00276,0.02329],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.04419,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":169.0,"n_steps_budget":600.0,"object_pos_end":[0.57255,-0.06357,0.02526],"object_pos_start":[0.55344,-0.03495,0.02413],"object_to_goal_dist_end":0.11284,"object_to_goal_dist_start":0.12686,"object_z_max":0.02573,"peak_contact_force":54.13058,"phase_name":"push_forward","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":641.0,"raw_peak_contact_force":97.24403,"subtask_id":"push_toward_goal","tcp_end":[0.54145,-0.03183,0.02122],"tcp_start":[0.52317,-0.00276,0.02329],"tcp_to_object_dist_end":0.04462,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1c6409cc6d884b90ecc3937d36e5ea87cc4ef513b6f301a9da66b4e84390f805`; realized-scene SHA-256: `5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.50458,-0.01881,0.025]}],"axes":[{"name":"push_direction","value":[-0.00458,-0.13119,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.50458,-0.01881,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.86765,"average_solve_count":68.0,"average_success_count":68.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"arc_behind.approach_speed":0.2743,"arc_behind.approach_tolerance":0.00969,"arc_behind.arc_height":0.12833,"push_forward.push_distance":0.21453,"push_forward.push_speed":0.05456,"push_forward.push_tolerance":0.02614},"optimized_scores":{"best_composite_score":0.2456,"best_fitness_score":0.5456,"best_task_score":0.74463},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":2130.0,"contact_point_centroid":[0.50506,-0.02129,-1e-05],"force_p95":0.94903,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":116.96779,"mean_force":1.66465,"phase_index":0.0,"phase_name":"arc_behind","phase_type":"approach","tcp_position_centroid":[0.49902,0.05231,0.16787]},{"body_a":"attachment","body_b":"push_box","contact_count":72.0,"contact_point_centroid":[0.50993,-0.03138,0.047],"force_p95":89.77096,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":108.16548,"mean_force":26.06435,"phase_index":0.0,"phase_name":"arc_behind","phase_type":"approach","tcp_position_centroid":[0.49962,-0.01997,0.02841]},{"body_a":"push_box","body_b":"link7","contact_count":27.0,"contact_point_centroid":[0.53758,-0.05595,0.05019],"force_p95":89.2146,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":97.908,"mean_force":44.91205,"phase_index":0.0,"phase_name":"arc_behind","phase_type":"approach","tcp_position_centroid":[0.49982,-0.03618,0.0234]},{"body_a":"world","body_b":"push_box","contact_count":1811.0,"contact_point_centroid":[0.51403,-0.12008,-4e-05],"force_p95":0.35927,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.67622,"mean_force":0.27611,"phase_index":1.0,"phase_name":"push_forward","phase_type":"push","tcp_position_centroid":[0.52124,0.00286,0.02913]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.52018,-0.06214,0.05058],"force_p95":0.0,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"push_forward","phase_type":"push","tcp_position_centroid":[0.50073,-0.05169,0.02289]}],"total_contact_groups":5},"final_pose_error":0.01484,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51431,-0.11968,0.02499],"final_tcp_position":[0.54133,0.04807,0.03786],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":116.96779,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":617.0,"n_steps_budget":660.0,"object_pos_end":[0.51311,-0.0952,0.0304],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.0566,"object_to_goal_dist_start":0.13127,"object_z_max":0.03035,"peak_contact_force":0.10945,"phase_name":"arc_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2229.0,"raw_peak_contact_force":116.96779,"subtask_id":"approach_pre_contact","tcp_end":[0.50073,-0.05169,0.02289],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.04586,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":492.0,"n_steps_budget":1000.0,"object_pos_end":[0.51431,-0.11968,0.02499],"object_pos_start":[0.51311,-0.0952,0.0304],"object_to_goal_dist_end":0.03352,"object_to_goal_dist_start":0.0566,"object_z_max":0.03041,"peak_contact_force":0.24525,"phase_name":"push_forward","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1812.0,"raw_peak_contact_force":4.67622,"subtask_id":"push_toward_goal","tcp_end":[0.54133,0.04807,0.03786],"tcp_start":[0.50073,-0.05169,0.02289],"tcp_to_object_dist_end":0.17041,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f52ec1899e2888770a8b6b3ae605718303ef4b10e72cfd7d20ce53303721b2b0`; realized-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.51501,0.04767,0.025]}],"axes":[{"name":"push_direction","value":[-0.01501,-0.19767,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.51501,0.04767,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.71795,"average_solve_count":117.0,"average_success_count":117.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"arc_behind.approach_speed":0.05578,"arc_behind.approach_tolerance":0.02014,"arc_behind.arc_height":0.12845,"push_forward.push_distance":0.26303,"push_forward.push_speed":0.05043,"push_forward.push_tolerance":0.01965},"optimized_scores":{"best_composite_score":-0.13803,"best_fitness_score":0.16197,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":176.0,"contact_point_centroid":[0.52367,0.0619,0.04723],"force_p95":231.96769,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":241.25285,"mean_force":188.49143,"phase_index":0.0,"phase_name":"arc_behind","phase_type":"approach","tcp_position_centroid":[0.5126,0.06191,0.05025]},{"body_a":"attachment","body_b":"push_box","contact_count":397.0,"contact_point_centroid":[0.53813,0.07183,0.04485],"force_p95":195.96923,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":220.29303,"mean_force":176.63559,"phase_index":1.0,"phase_name":"push_forward","phase_type":"push","tcp_position_centroid":[0.52899,0.07689,0.04656]},{"body_a":"world","body_b":"push_box","contact_count":903.0,"contact_point_centroid":[0.52222,0.06432,-0.0008],"force_p95":177.44557,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":201.04749,"mean_force":78.3072,"phase_index":1.0,"phase_name":"push_forward","phase_type":"push","tcp_position_centroid":[0.52833,0.07455,0.04684]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.51523,0.04722,-8e-05],"force_p95":72.91846,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":104.79913,"mean_force":8.57213,"phase_index":0.0,"phase_name":"arc_behind","phase_type":"approach","tcp_position_centroid":[0.50324,0.0802,0.17039]}],"total_contact_groups":4},"final_pose_error":0.01471,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51895,0.06658,0.035],"final_tcp_position":[0.52917,0.10708,0.03638],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":241.25285,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51786,0.04275,0.0238],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19358,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":230.89569,"phase_name":"arc_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4176.0,"raw_peak_contact_force":241.25285,"subtask_id":"approach_pre_contact","tcp_end":[0.51878,0.05108,0.0486],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.02618,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":397.0,"n_steps_budget":840.0,"object_pos_end":[0.51895,0.06658,0.035],"object_pos_start":[0.51786,0.04275,0.0238],"object_to_goal_dist_end":0.21764,"object_to_goal_dist_start":0.19358,"object_z_max":0.0349,"peak_contact_force":73.69166,"phase_name":"push_forward","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1300.0,"raw_peak_contact_force":220.29303,"subtask_id":"push_toward_goal","tcp_end":[0.52917,0.10708,0.03638],"tcp_start":[0.51878,0.05108,0.0486],"tcp_to_object_dist_end":0.04179,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```