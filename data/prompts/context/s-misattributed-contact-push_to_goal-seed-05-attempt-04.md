## Search State

- **Seed**: 5
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | time_limit | 6 | 0.3069 | 0.67 | ✅ accepted |
| 3 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | time_limit | 6 | 0.2620 | 0.63 | ✅ accepted |
| 2 | push → release → pull → release → release → grasp → retract | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | admittance_control | position_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | time_limit | time_limit | pose_tolerance | 3 | -0.3000 | 0.00 | ❌ rejected |
| 1 | push → release → pull → release → release → grasp → retract | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | admittance_control | position_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | time_limit | time_limit | pose_tolerance | 3 | -0.3000 | 0.00 | ❌ rejected |
| 0 | push → release → pull → release → release → grasp → retract | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | admittance_control | position_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | time_limit | time_limit | pose_tolerance | 3 | -0.3000 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.67 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.307) — your mutation base

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
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - -0.275
    offset_along_axis:
      distance: 0.03
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: negative
    orientation:
      mode: none
  parameters:
    approach_offset:
      type: scalar
      range:
      - 0.01
      - 0.06
      default: 0.03
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
  subtask_id: pre_contact
- id: push_1
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
      mode: replace_offset_projection
      sign: positive
    orientation:
      mode: none
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.4
      default: 0.2
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
    push_time:
      type: scalar
      range:
      - 3.0
      - 10.0
      default: 6
      binds_to:
      - path: duration.max_time
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
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, -0.275], offset_along_axis={axis=task_goal_direction, distance=0.03, mode=replace_offset_projection, sign=negative}
  - orientation: mode=none
  - parameter_bindings:
    - approach_offset: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.2, mode=replace_offset_projection, sign=positive}
  - orientation: mode=none
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_time: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=contact_check, when=during_phase, predicate=contact_detected, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.005, 0.0]

## Design Metrics

- **Composite score**: 0.307
- **task_score** (E): 0.668
- **fitness_score**: 0.607  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.300

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.00 | 0.33 | 0.3074 |
| push_1 | 1.00 | 1.00 | 0.1908 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.558, 0.050, 0.007) | (0.519, 0.022, 0.025)→(0.533, 0.020, 0.026) | 0.173→0.174 | 0.33 / 1.333 | 0.082 | 113.489 |
| push_1 | push | 1.00 / time_limit | (0.558, 0.050, 0.007)→(0.505, -0.131, 0.011) | (0.533, 0.020, 0.026)→(0.476, -0.107, 0.025) | 0.174→0.059 | 1.00 / 3.333 | 102.522 | 351.591 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.715
- goal_progress: 0.813
- terminal_score: 0.813
- phase_score: 0.638
- phase_breakdown.push_to_goal_score: 0.819
- phase_breakdown.pre_contact_score: 0.215

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.708
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.813
- **Median Q (composite search score)**: 0.371
- **K-run variance**: 0.0139
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.353


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.67949,"average_solve_count":78.0,"average_success_count":78.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_offset":0.05312,"approach_1.approach_speed":0.19782,"approach_1.approach_tolerance":0.01384,"push_1.push_distance":0.19282,"push_1.push_speed":0.14599,"push_1.push_time":5.89605},"optimized_scores":{"best_composite_score":0.40815,"best_fitness_score":0.70815,"best_task_score":0.81311},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":60.0,"contact_point_centroid":[0.58829,0.04211,0.04625],"force_p95":303.48186,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":500.96013,"mean_force":172.59849,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.60451,0.06337,0.00309]},{"body_a":"attachment","body_b":"world","contact_count":33.0,"contact_point_centroid":[0.61446,0.05966,-0.00125],"force_p95":411.55997,"geom_a":"pusher_tip","geom_b":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":435.82694,"mean_force":203.17259,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.60305,0.06314,-0.00127]},{"body_a":"attachment","body_b":"push_box","contact_count":371.0,"contact_point_centroid":[0.5616,0.04605,0.0458],"force_p95":288.37949,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":318.64279,"mean_force":229.49942,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.55954,0.04951,0.04492]},{"body_a":"world","body_b":"push_box","contact_count":3318.0,"contact_point_centroid":[0.54338,0.03802,-0.00033],"force_p95":157.69367,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":297.74844,"mean_force":29.13846,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52298,0.02843,0.13529]},{"body_a":"push_box","body_b":"link7","contact_count":879.0,"contact_point_centroid":[0.56315,-0.03318,0.04917],"force_p95":97.12755,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":113.77773,"mean_force":52.61903,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.56716,-0.01863,0.00659]},{"body_a":"world","body_b":"push_box","contact_count":1632.0,"contact_point_centroid":[0.5415,-0.0511,-0.00021],"force_p95":77.36168,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":94.68344,"mean_force":32.40432,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.564,-0.02542,0.00659]},{"body_a":"attachment","body_b":"push_box","contact_count":655.0,"contact_point_centroid":[0.55048,-0.04831,0.00883],"force_p95":34.7597,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.14043,"mean_force":19.916,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.55768,-0.0396,0.00694]}],"total_contact_groups":7},"final_pose_error":0.20116,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.46478,-0.14477,0.02505],"final_tcp_position":[0.50935,-0.14515,0.00737],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":500.96013,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56731,0.03528,0.02853],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.19716,"object_to_goal_dist_start":0.1905,"object_z_max":0.03546,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3166.0,"raw_peak_contact_force":113.77773,"subtask_id":"pre_contact","tcp_end":[0.60403,0.06571,0.00212],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.05451,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46478,-0.14477,0.02505],"object_pos_start":[0.56731,0.03528,0.02853],"object_to_goal_dist_end":0.0356,"object_to_goal_dist_start":0.19716,"object_z_max":0.03024,"peak_contact_force":183.66322,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3782.0,"raw_peak_contact_force":500.96013,"subtask_id":"push_to_goal","tcp_end":[0.50935,-0.14515,0.00737],"tcp_start":[0.60403,0.06571,0.00212],"tcp_to_object_dist_end":0.04794,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92135,"average_solve_count":89.0,"average_success_count":89.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_offset":0.04895,"approach_1.approach_speed":0.11472,"approach_1.approach_tolerance":0.00864,"push_1.push_distance":0.16716,"push_1.push_speed":0.07276,"push_1.push_time":6.50034},"optimized_scores":{"best_composite_score":0.37081,"best_fitness_score":0.67081,"best_task_score":0.71405},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":61.0,"contact_point_centroid":[0.50691,0.00577,0.04671],"force_p95":209.31247,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":244.97728,"mean_force":122.35001,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50126,0.01467,0.04856]},{"body_a":"world","body_b":"push_box","contact_count":3878.0,"contact_point_centroid":[0.50506,-0.019,-3e-05],"force_p95":8.72714,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":182.04009,"mean_force":2.68367,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49879,0.00764,0.15793]},{"body_a":"push_box","body_b":"link7","contact_count":20.0,"contact_point_centroid":[0.53058,-0.0034,0.04884],"force_p95":121.67079,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":122.40697,"mean_force":96.46661,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50044,0.01573,0.01794]},{"body_a":"world","body_b":"push_box","contact_count":2115.0,"contact_point_centroid":[0.49254,-0.08166,-0.00012],"force_p95":54.49812,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":73.60379,"mean_force":14.6271,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49822,-0.03931,0.01515]},{"body_a":"push_box","body_b":"link7","contact_count":623.0,"contact_point_centroid":[0.52301,-0.03774,0.0498],"force_p95":60.51922,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":66.88895,"mean_force":36.6888,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50007,-0.01669,0.01576]},{"body_a":"attachment","body_b":"push_box","contact_count":843.0,"contact_point_centroid":[0.50775,-0.04601,0.03534],"force_p95":40.43359,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.10488,"mean_force":20.24965,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49864,-0.0344,0.01528]}],"total_contact_groups":6},"final_pose_error":0.21477,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.46766,-0.13094,0.02506],"final_tcp_position":[0.49429,-0.1025,0.01457],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":244.97728,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5056,-0.0215,0.02476],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.12862,"object_to_goal_dist_start":0.13127,"object_z_max":0.02508,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3581.0,"raw_peak_contact_force":73.60379,"subtask_id":"pre_contact","tcp_end":[0.50171,0.0159,0.01625],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.03856,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46766,-0.13094,0.02506],"object_pos_start":[0.5056,-0.0215,0.02476],"object_to_goal_dist_end":0.03754,"object_to_goal_dist_start":0.12862,"object_z_max":0.02576,"peak_contact_force":122.40697,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3959.0,"raw_peak_contact_force":244.97728,"subtask_id":"push_to_goal","tcp_end":[0.49429,-0.1025,0.01457],"tcp_start":[0.50171,0.0159,0.01625],"tcp_to_object_dist_end":0.04035,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.94595,"average_solve_count":111.0,"average_success_count":111.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_offset":0.05758,"approach_1.approach_speed":0.08122,"approach_1.approach_tolerance":0.02012,"push_1.push_distance":0.13569,"push_1.push_speed":0.13778,"push_1.push_time":9.94776},"optimized_scores":{"best_composite_score":0.14181,"best_fitness_score":0.44181,"best_task_score":0.47652},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":500.0,"contact_point_centroid":[0.54332,0.05268,0.04515],"force_p95":284.79339,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":308.83572,"mean_force":222.33719,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.54103,0.05726,0.04415]},{"body_a":"push_box","body_b":"link7","contact_count":17.0,"contact_point_centroid":[0.55565,0.06534,0.05868],"force_p95":290.60244,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":296.31485,"mean_force":59.97229,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.57611,0.06861,0.0135]},{"body_a":"world","body_b":"push_box","contact_count":3135.0,"contact_point_centroid":[0.52198,0.04899,-0.00035],"force_p95":136.74,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":223.66467,"mean_force":36.14991,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51505,0.03511,0.12754]},{"body_a":"push_box","body_b":"link7","contact_count":715.0,"contact_point_centroid":[0.53737,0.01044,0.05253],"force_p95":89.30818,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":153.08575,"mean_force":49.94706,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.55044,-0.00266,0.00621]},{"body_a":"attachment","body_b":"world","contact_count":24.0,"contact_point_centroid":[0.57891,0.06587,-0.00062],"force_p95":109.96617,"geom_a":"pusher_tip","geom_b":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":110.46586,"mean_force":67.46315,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.56721,0.06755,0.00086]},{"body_a":"world","body_b":"push_box","contact_count":2058.0,"contact_point_centroid":[0.50737,-0.01576,-0.00024],"force_p95":73.04921,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":98.93324,"mean_force":18.37942,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53741,-0.04886,0.00738]},{"body_a":"attachment","body_b":"push_box","contact_count":152.0,"contact_point_centroid":[0.54366,0.0104,0.00828],"force_p95":29.69545,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.59223,"mean_force":14.70446,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.55467,0.01402,0.00596]}],"total_contact_groups":7},"final_pose_error":0.14202,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49486,-0.04635,0.02499],"final_tcp_position":[0.51088,-0.14625,0.01089],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":308.83572,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52706,0.0452,0.02432],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19707,"object_to_goal_dist_start":0.19823,"object_z_max":0.03628,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2949.0,"raw_peak_contact_force":153.08575,"subtask_id":"pre_contact","tcp_end":[0.56822,0.06861,0.00172],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.05246,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49486,-0.04635,0.02499],"object_pos_start":[0.52706,0.0452,0.02432],"object_to_goal_dist_end":0.10377,"object_to_goal_dist_start":0.19707,"object_z_max":0.03533,"peak_contact_force":1.49528,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3652.0,"raw_peak_contact_force":308.83572,"subtask_id":"push_to_goal","tcp_end":[0.51088,-0.14625,0.01089],"tcp_start":[0.56822,0.06861,0.00172],"tcp_to_object_dist_end":0.10215,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```