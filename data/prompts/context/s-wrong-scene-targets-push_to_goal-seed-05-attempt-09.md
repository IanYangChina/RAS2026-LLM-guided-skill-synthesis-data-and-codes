## Search State

- **Seed**: 5
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → push | arc_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | time_limit | 4 | 0.5326 | 0.81 | ❌ rejected |
| 8 | approach → push | arc_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | time_limit | 4 | 0.5133 | 0.78 | ❌ rejected |
| 7 | approach → push | arc_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | time_limit | 4 | 0.5284 | 0.81 | ❌ rejected |
| 6 | approach → push | arc_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | time_limit | 4 | 0.5419 | 0.82 | ✅ accepted |
| 5 | push → release → pull → release → release → grasp → retract | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | admittance_control | position_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | time_limit | time_limit | pose_tolerance | 3 | -0.3000 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.81 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.533) — your mutation base

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

- **Composite score**: 0.533
- **task_score** (E): 0.807
- **fitness_score**: 0.733  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.200

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| arc_behind | 1.00 | 1.00 | 0.2793 |
| push_forward | 1.00 | 1.00 | 0.1551 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| arc_behind | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.518, 0.065, 0.031) | (0.519, 0.022, 0.025)→(0.519, 0.022, 0.025) | 0.173→0.173 | 1.00 / 4.000 | 0.245 | 0.245 |
| push_forward | push | 1.00 / time_limit | (0.518, 0.065, 0.031)→(0.503, -0.089, 0.027) | (0.519, 0.022, 0.025)→(0.521, -0.121, 0.030) | 0.173→0.037 | 1.00 / 3.000 | 47.075 | 62.761 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.990
- lateral_force_integral: None
- approach_alignment: 0.687
- goal_progress: 0.982
- terminal_score: 0.982
- phase_score: 0.790
- phase_breakdown.push_toward_goal_score: 0.982
- phase_breakdown.approach_pre_contact_score: 0.343

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.867
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.982
- **Median Q (composite search score)**: 0.489
- **K-run variance**: 0.0094
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.555


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.36765,"average_solve_count":68.0,"average_success_count":68.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"arc_behind.approach_speed":0.1927,"arc_behind.arc_height":0.03655,"push_forward.push_distance":0.39937,"push_forward.push_speed":0.01182},"optimized_scores":{"best_composite_score":0.44215,"best_fitness_score":0.64215,"best_task_score":0.69309},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":556.0,"contact_point_centroid":[0.55325,-0.04836,0.05704],"force_p95":81.14809,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":97.6856,"mean_force":48.70914,"phase_index":1.0,"phase_name":"push_forward","phase_type":"push","tcp_position_centroid":[0.5149,-0.04004,0.02931]},{"body_a":"world","body_b":"push_box","contact_count":1708.0,"contact_point_centroid":[0.54623,-0.0539,-0.00014],"force_p95":64.21644,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":87.43755,"mean_force":23.2833,"phase_index":1.0,"phase_name":"push_forward","phase_type":"push","tcp_position_centroid":[0.51998,-0.0084,0.02875]},{"body_a":"attachment","body_b":"push_box","contact_count":870.0,"contact_point_centroid":[0.53337,-0.01977,0.048],"force_p95":65.98174,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":78.26824,"mean_force":25.69608,"phase_index":1.0,"phase_name":"push_forward","phase_type":"push","tcp_position_centroid":[0.51937,-0.0106,0.02849]},{"body_a":"world","body_b":"push_box","contact_count":3400.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"arc_behind","phase_type":"approach","tcp_position_centroid":[0.51688,0.05888,0.1733]}],"total_contact_groups":4},"final_pose_error":0.46418,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.54072,-0.1086,0.03179],"final_tcp_position":[0.50937,-0.08585,0.03147],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":97.6856,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":850.0,"n_steps_budget":960.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"arc_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3400.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_pre_contact","tcp_end":[0.53799,0.07787,0.03239],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.04161,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54072,-0.1086,0.03179],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.05847,"object_to_goal_dist_start":0.1905,"object_z_max":0.03186,"peak_contact_force":83.98204,"phase_name":"push_forward","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3134.0,"raw_peak_contact_force":97.6856,"subtask_id":"push_toward_goal","tcp_end":[0.50937,-0.08585,0.03147],"tcp_start":[0.53799,0.07787,0.03239],"tcp_to_object_dist_end":0.03875,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.42667,"average_solve_count":75.0,"average_success_count":75.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"arc_behind.approach_speed":0.1487,"arc_behind.arc_height":0.0783,"push_forward.push_distance":0.15062,"push_forward.push_speed":0.08694},"optimized_scores":{"best_composite_score":0.66698,"best_fitness_score":0.86698,"best_task_score":0.98191},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":779.0,"contact_point_centroid":[0.50673,-0.05974,0.04255],"force_p95":18.22002,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.63839,"mean_force":5.92511,"phase_index":1.0,"phase_name":"push_forward","phase_type":"push","tcp_position_centroid":[0.496,-0.04792,0.02238]},{"body_a":"world","body_b":"push_box","contact_count":1542.0,"contact_point_centroid":[0.50628,-0.08167,-5e-05],"force_p95":13.29932,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.33519,"mean_force":3.9453,"phase_index":1.0,"phase_name":"push_forward","phase_type":"push","tcp_position_centroid":[0.49678,-0.02779,0.02299]},{"body_a":"push_box","body_b":"link7","contact_count":220.0,"contact_point_centroid":[0.52786,-0.07825,0.0515],"force_p95":11.50844,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.50975,"mean_force":4.63718,"phase_index":1.0,"phase_name":"push_forward","phase_type":"push","tcp_position_centroid":[0.49579,-0.06146,0.02229]},{"body_a":"world","body_b":"push_box","contact_count":3852.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"arc_behind","phase_type":"approach","tcp_position_centroid":[0.49984,0.0601,0.1702]}],"total_contact_groups":4},"final_pose_error":0.18849,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50123,-0.14876,0.02661],"final_tcp_position":[0.49494,-0.11207,0.02188],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":26.63839,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":963.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"arc_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3852.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_pre_contact","tcp_end":[0.50158,0.02965,0.02767],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.04862,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50123,-0.14876,0.02661],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.00237,"object_to_goal_dist_start":0.13127,"object_z_max":0.02673,"peak_contact_force":0.16275,"phase_name":"push_forward","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2541.0,"raw_peak_contact_force":26.63839,"subtask_id":"push_toward_goal","tcp_end":[0.49494,-0.11207,0.02188],"tcp_start":[0.50158,0.02965,0.02767],"tcp_to_object_dist_end":0.03753,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.34848,"average_solve_count":66.0,"average_success_count":66.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"arc_behind.approach_speed":0.19994,"arc_behind.arc_height":0.02885,"push_forward.push_distance":0.06216,"push_forward.push_speed":0.09989},"optimized_scores":{"best_composite_score":0.48867,"best_fitness_score":0.68867,"best_task_score":0.74701},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":414.0,"contact_point_centroid":[0.53446,-0.04678,0.05679],"force_p95":50.10335,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":63.95868,"mean_force":24.92301,"phase_index":1.0,"phase_name":"push_forward","phase_type":"push","tcp_position_centroid":[0.50324,-0.03327,0.02666]},{"body_a":"attachment","body_b":"push_box","contact_count":819.0,"contact_point_centroid":[0.51789,-0.00749,0.04668],"force_p95":50.25882,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":60.20204,"mean_force":15.55371,"phase_index":1.0,"phase_name":"push_forward","phase_type":"push","tcp_position_centroid":[0.50483,0.00323,0.02719]},{"body_a":"world","body_b":"push_box","contact_count":1480.0,"contact_point_centroid":[0.52446,-0.04493,-9e-05],"force_p95":33.78506,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":51.04561,"mean_force":12.63328,"phase_index":1.0,"phase_name":"push_forward","phase_type":"push","tcp_position_centroid":[0.5053,0.00768,0.02755]},{"body_a":"world","body_b":"push_box","contact_count":3260.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"arc_behind","phase_type":"approach","tcp_position_centroid":[0.50525,0.0589,0.17331]}],"total_contact_groups":4},"final_pose_error":0.143,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51971,-0.10424,0.03067],"final_tcp_position":[0.50339,-0.06923,0.02749],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":63.95868,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":815.0,"n_steps_budget":900.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"arc_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3260.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_pre_contact","tcp_end":[0.51307,0.08741,0.03363],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.04072,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51971,-0.10424,0.03067],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.05015,"object_to_goal_dist_start":0.19823,"object_z_max":0.03067,"peak_contact_force":57.07909,"phase_name":"push_forward","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2713.0,"raw_peak_contact_force":63.95868,"subtask_id":"push_toward_goal","tcp_end":[0.50339,-0.06923,0.02749],"tcp_start":[0.51307,0.08741,0.03363],"tcp_to_object_dist_end":0.03876,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```