## Search State

- **Seed**: 3
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1602 | 0.38 | ✅ accepted |
| 10 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | -0.0380 | 0.16 | ❌ rejected |
| 9 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1518 | 0.37 | ❌ rejected |
| 8 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1459 | 0.36 | ❌ rejected |
| 7 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1757 | 0.37 | ❌ rejected |

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
- Frozen realised-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`
- Frozen object start: [0.45027790005723495, -0.03158273920846803, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.45027790005723495, -0.03158273920846803, 0.025)
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
  frozen_object_start: [0.4503, -0.0316, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.45027790005723495, -0.03158273920846803, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [0.0497, -0.1184, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be

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
| `object` | offset from object initial position (0.45027790005723495, -0.03158273920846803, 0.025) | approach/contact targets near object start |
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

## Current Skill (Q=0.160) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: reach_object
  anchor: object
  offset:
  - -0.025
  - 0.0
  - 0.1
  weight: 0.4
- id: push_to_goal
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
    - -0.025
    - 0.0
    - 0.1
    tolerance: 0.02
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.speed
        mode: add
  subtask_id: reach_object
- id: descend_side
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - -0.025
    - 0.0
    - 0.0
    tolerance: 0.01
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: add
  subtask_id: reach_object
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
    tolerance: 0.02
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: add
  guards:
  - id: contact_ok
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
- **approach_side** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[-0.025, 0.0, 0.1], tolerance=0.02
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (add)
- **descend_side** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[-0.025, 0.0, 0.0], tolerance=0.01
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (add)
- **push_to_goal** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (add)
  - guards:
    - id=contact_ok, when=during_phase, predicate=contact_detected, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.005, 0.0]

## Design Metrics

- **Composite score**: 0.160
- **task_score** (E): 0.381
- **fitness_score**: 0.340  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.180

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_side | 1.00 | 1.00 | 0.1643 |
| descend_side | 1.00 | 1.00 | 0.0963 |
| push_to_goal | 1.00 | 1.00 | 0.1415 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_side | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.487, 0.002, 0.143) | (0.513, 0.002, 0.025)→(0.513, 0.002, 0.025) | 0.160→0.160 | 1.00 / 5.000 | 259.844 | 293.731 |
| descend_side | descend | 1.00 / step_budget | (0.487, 0.002, 0.143)→(0.502, 0.002, 0.048) | (0.513, 0.002, 0.025)→(0.517, 0.002, 0.024) | 0.160→0.160 | 1.00 / 4.000 | 0.303 | 221.978 |
| push_to_goal | push | 1.00 / step_budget | (0.502, 0.002, 0.048)→(0.496, -0.131, 0.024) | (0.517, 0.002, 0.024)→(0.517, -0.057, 0.025) | 0.160→0.101 | 1.00 / 4.000 | 0.245 | 0.245 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.486
- lateral_force_integral: None
- approach_alignment: 0.694
- goal_progress: 0.483
- terminal_score: 0.483
- phase_score: 0.370
- phase_breakdown.push_to_goal_score: 0.476
- phase_breakdown.reach_object_score: 0.212

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.416
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.483
- **Median Q (composite search score)**: 0.146
- **K-run variance**: 0.0032
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.516


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `01fea9f27a58d64b0f9b0ff0cae1096a52b0da1ad311c77058a75ddb9aab77d2`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `c53c9bf1992485fcf877d50f4ee23d3483b4b9e63e5a19adda2461c26d89c46e`; realized-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45028,-0.03158,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.04972,-0.11842,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.45028,-0.03158,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.68182,"average_solve_count":88.0,"average_success_count":88.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_side.approach_speed":0.18392,"descend_side.descend_speed":0.05875,"push_to_goal.push_speed":0.1262},"optimized_scores":{"best_composite_score":0.23551,"best_fitness_score":0.41551,"best_task_score":0.48327},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":234.0,"contact_point_centroid":[0.47186,-0.06093,0.04457],"force_p95":273.94658,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":312.77825,"mean_force":197.41581,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.46383,-0.06569,0.04708]},{"body_a":"attachment","body_b":"push_box","contact_count":210.0,"contact_point_centroid":[0.44306,-0.03166,0.04612],"force_p95":303.37748,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":312.48143,"mean_force":270.69149,"phase_index":1.0,"phase_name":"descend_side","phase_type":"descend","tcp_position_centroid":[0.43308,-0.03142,0.05021]},{"body_a":"world","body_b":"push_box","contact_count":602.0,"contact_point_centroid":[0.46456,-0.05802,-0.00086],"force_p95":227.98706,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":277.22404,"mean_force":77.77597,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.46417,-0.07031,0.04424]},{"body_a":"world","body_b":"push_box","contact_count":2088.0,"contact_point_centroid":[0.45107,-0.03167,-0.00026],"force_p95":84.09613,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":93.58303,"mean_force":27.47566,"phase_index":1.0,"phase_name":"descend_side","phase_type":"descend","tcp_position_centroid":[0.42946,-0.02987,0.07982]},{"body_a":"world","body_b":"push_box","contact_count":1228.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_side","phase_type":"approach","tcp_position_centroid":[0.46664,-0.01334,0.22266]}],"total_contact_groups":5},"final_pose_error":0.01992,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47026,-0.09068,0.02397],"final_tcp_position":[0.48928,-0.13321,0.02528],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":312.77825,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":307.0,"n_steps_budget":690.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":280.02517,"phase_name":"approach_side","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2298.0,"raw_peak_contact_force":312.48143,"subtask_id":"reach_object","tcp_end":[0.43226,-0.02753,0.14318],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11963,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":522.0,"n_steps_budget":1000.0,"object_pos_end":[0.45402,-0.03202,0.02358],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12663,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":0.41783,"phase_name":"descend_side","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":836.0,"raw_peak_contact_force":312.77825,"subtask_id":"reach_object","tcp_end":[0.442,-0.0324,0.04925],"tcp_start":[0.43226,-0.02753,0.14318],"tcp_to_object_dist_end":0.02835,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":292.0,"n_steps_budget":690.0,"object_pos_end":[0.47026,-0.09068,0.02397],"object_pos_start":[0.45402,-0.03202,0.02358],"object_to_goal_dist_end":0.06636,"object_to_goal_dist_start":0.12663,"object_z_max":0.0344,"peak_contact_force":0.24525,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1228.0,"raw_peak_contact_force":0.24534,"subtask_id":"push_to_goal","tcp_end":[0.48928,-0.13321,0.02528],"tcp_start":[0.442,-0.0324,0.04925],"tcp_to_object_dist_end":0.04661,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `234a0edc218dcf63b67654ddcfd8b0f12da84040687f62c4c4845001a50f549a`; realized-scene SHA-256: `721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.55317,0.00136,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.05317,-0.15136,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.55317,0.00136,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.14085,"average_solve_count":71.0,"average_success_count":71.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_side.approach_speed":0.27683,"descend_side.descend_speed":0.13456,"push_to_goal.push_speed":0.10536},"optimized_scores":{"best_composite_score":0.14576,"best_fitness_score":0.32576,"best_task_score":0.36019},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":98.0,"contact_point_centroid":[0.54039,0.00123,0.04694],"force_p95":280.83829,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":295.8284,"mean_force":237.97822,"phase_index":1.0,"phase_name":"descend_side","phase_type":"descend","tcp_position_centroid":[0.52921,0.00121,0.04927]},{"body_a":"attachment","body_b":"push_box","contact_count":278.0,"contact_point_centroid":[0.54425,-0.02508,0.0467],"force_p95":173.16398,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":177.25371,"mean_force":139.91368,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.53508,-0.03001,0.04868]},{"body_a":"world","body_b":"push_box","contact_count":971.0,"contact_point_centroid":[0.55154,-0.03341,-0.00051],"force_p95":127.74357,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":135.31437,"mean_force":41.50478,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.52532,-0.05643,0.04099]},{"body_a":"world","body_b":"push_box","contact_count":1468.0,"contact_point_centroid":[0.55358,0.00136,-0.00014],"force_p95":70.18473,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":89.51477,"mean_force":16.13727,"phase_index":1.0,"phase_name":"descend_side","phase_type":"descend","tcp_position_centroid":[0.52314,0.00114,0.0853]},{"body_a":"push_box","body_b":"link7","contact_count":44.0,"contact_point_centroid":[0.55295,-0.06023,0.06511],"force_p95":39.30317,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.40379,"mean_force":20.60699,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.51814,-0.0826,0.03563]},{"body_a":"world","body_b":"push_box","contact_count":1148.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24532,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_side","phase_type":"approach","tcp_position_centroid":[0.51011,0.00054,0.22302]}],"total_contact_groups":6},"final_pose_error":0.01984,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.54659,-0.05854,0.02495],"final_tcp_position":[0.50124,-0.13029,0.0231],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":295.8284,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":287.0,"n_steps_budget":600.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":255.59177,"phase_name":"approach_side","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1566.0,"raw_peak_contact_force":295.8284,"subtask_id":"reach_object","tcp_end":[0.5217,0.00111,0.14342],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12254,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":367.0,"n_steps_budget":600.0,"object_pos_end":[0.55623,0.00136,0.0237],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16148,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":0.24482,"phase_name":"descend_side","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1293.0,"raw_peak_contact_force":177.25371,"subtask_id":"reach_object","tcp_end":[0.53722,0.00124,0.04761],"tcp_start":[0.5217,0.00111,0.14342],"tcp_to_object_dist_end":0.03055,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":411.0,"n_steps_budget":930.0,"object_pos_end":[0.54659,-0.05854,0.02495],"object_pos_start":[0.55623,0.00136,0.0237],"object_to_goal_dist_end":0.10264,"object_to_goal_dist_start":0.16148,"object_z_max":0.03486,"peak_contact_force":0.24525,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1148.0,"raw_peak_contact_force":0.24534,"subtask_id":"push_to_goal","tcp_end":[0.50124,-0.13029,0.0231],"tcp_start":[0.53722,0.00124,0.04761],"tcp_to_object_dist_end":0.0849,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `107d1233d3b0a09f0fa34aa18231b315c9a1d92237bb254399d486ed8004836a`; realized-scene SHA-256: `b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5366,0.03695,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.0366,-0.18695,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5366,0.03695,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.8913,"average_solve_count":92.0,"average_success_count":92.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_side.approach_speed":0.2265,"descend_side.descend_speed":0.06262,"push_to_goal.push_speed":0.12085},"optimized_scores":{"best_composite_score":0.09948,"best_fitness_score":0.27948,"best_task_score":0.29942},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":183.0,"contact_point_centroid":[0.52767,0.03642,0.0467],"force_p95":264.79611,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":272.88334,"mean_force":233.87827,"phase_index":1.0,"phase_name":"descend_side","phase_type":"descend","tcp_position_centroid":[0.51662,0.03635,0.04917]},{"body_a":"attachment","body_b":"push_box","contact_count":265.0,"contact_point_centroid":[0.53472,0.00943,0.0473],"force_p95":173.11553,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":175.90264,"mean_force":130.5093,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.52579,0.00404,0.0488]},{"body_a":"world","body_b":"push_box","contact_count":1312.0,"contact_point_centroid":[0.53717,-0.00502,-0.00033],"force_p95":93.49685,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":101.10541,"mean_force":26.75185,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.51428,-0.04682,0.03726]},{"body_a":"world","body_b":"push_box","contact_count":1908.0,"contact_point_centroid":[0.53742,0.03704,-0.00021],"force_p95":70.52907,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":75.11726,"mean_force":22.6817,"phase_index":1.0,"phase_name":"descend_side","phase_type":"descend","tcp_position_centroid":[0.5099,0.03452,0.07967]},{"body_a":"world","body_b":"push_box","contact_count":1156.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24532,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_side","phase_type":"approach","tcp_position_centroid":[0.50315,0.01541,0.22292]}],"total_contact_groups":5},"final_pose_error":0.01977,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53442,-0.02105,0.02499],"final_tcp_position":[0.49867,-0.13048,0.02216],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":272.88334,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":289.0,"n_steps_budget":600.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":243.91578,"phase_name":"approach_side","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2091.0,"raw_peak_contact_force":272.88334,"subtask_id":"reach_object","tcp_end":[0.50732,0.03182,0.1434],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12209,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":477.0,"n_steps_budget":1000.0,"object_pos_end":[0.54047,0.03739,0.02376],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.19172,"object_to_goal_dist_start":0.1905,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_side","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1577.0,"raw_peak_contact_force":175.90264,"subtask_id":"reach_object","tcp_end":[0.52564,0.03736,0.04816],"tcp_start":[0.50732,0.03182,0.1434],"tcp_to_object_dist_end":0.02856,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":471.0,"n_steps_budget":990.0,"object_pos_end":[0.53442,-0.02105,0.02499],"object_pos_start":[0.54047,0.03739,0.02376],"object_to_goal_dist_end":0.13346,"object_to_goal_dist_start":0.19172,"object_z_max":0.03493,"peak_contact_force":0.24525,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1156.0,"raw_peak_contact_force":0.24534,"subtask_id":"push_to_goal","tcp_end":[0.49867,-0.13048,0.02216],"tcp_start":[0.52564,0.03736,0.04816],"tcp_to_object_dist_end":0.11516,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```