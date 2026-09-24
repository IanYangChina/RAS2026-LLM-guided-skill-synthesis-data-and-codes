## Search State

- **Seed**: 3
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | admittance_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | 5 | 0.4366 | 0.88 | ✅ accepted |
| 9 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.4264 | 0.87 | ✅ accepted |
| 8 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.2674 | 0.73 | ❌ rejected |
| 7 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 5 | 0.4118 | 0.85 | ❌ rejected |
| 6 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | -0.2714 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.88 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.876, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.437) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: approach_target
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.3
- id: push_goal
  anchor: object
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_object
    entity: body
    offset:
    - 0.0
    - 0.0
    - 0.05
    offset_along_axis:
      distance: 0.1
      axis: task_goal_direction
      mode: add_to_offset
      sign: negative
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.03
      - 0.07
      default: 0.05
      binds_to:
      - path: target.offset.z
        mode: replace
    behind_distance_approach:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  subtask_id: approach_target
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_object
    entity: body
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.1
      axis: task_goal_direction
      mode: add_to_offset
      sign: negative
    orientation:
      mode: keep_current
  parameters:
    behind_distance_descend:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  subtask_id: approach_target
- id: push_1
  type: push
  generator: linear_cartesian
  control: admittance_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_object
    entity: body
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
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.08
      - 0.35
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.015
    - 0.015
    - 0.0
  subtask_id: push_goal
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.1
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=body, offset=[0.0, 0.0, 0.05], offset_along_axis={axis=task_goal_direction, distance=0.1, mode=add_to_offset, sign=negative}
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - behind_distance_approach: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=body, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.1, mode=add_to_offset, sign=negative}
  - orientation: mode=keep_current
  - parameter_bindings:
    - behind_distance_descend: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_object, entity=body, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.2, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=1, strategy=offset_target, offset=[0.015, 0.015, 0.0]
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.437
- **task_score** (E): 0.876
- **fitness_score**: 0.747  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1849 |
| descend_1 | 1.00 | 1.00 | 0.1156 |
| push_1 | 1.00 | 1.00 | 0.2102 |
| retract_1 | 1.00 | 1.00 | 0.0888 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / time_limit | (0.500, -0.000, 0.301)→(0.499, 0.068, 0.139) | (0.513, 0.002, 0.025)→(0.513, 0.002, 0.025) | 0.160→0.160 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_1 | descend | 1.00 / time_limit | (0.499, 0.068, 0.139)→(0.508, 0.080, 0.026) | (0.513, 0.002, 0.025)→(0.513, 0.002, 0.025) | 0.160→0.160 | 1.00 / 4.000 | 0.245 | 0.245 |
| push_1 | push | 1.00 / time_limit | (0.508, 0.080, 0.026)→(0.496, -0.120, 0.021) | (0.513, 0.002, 0.025)→(0.519, -0.147, 0.025) | 0.160→0.021 | 1.00 / 3.000 | 0.616 | 35.581 |
| retract_1 | retract | 1.00 / step_budget | (0.496, -0.120, 0.021)→(0.493, -0.118, 0.110) | (0.519, -0.147, 0.025)→(0.519, -0.147, 0.025) | 0.021→0.021 | 1.00 / 4.000 | 0.245 | 11.248 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.741
- goal_progress: 0.961
- terminal_score: 0.961
- phase_score: 0.747
- phase_breakdown.push_goal_score: 0.969
- phase_breakdown.approach_target_score: 0.229

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.833
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.961
- **Median Q (composite search score)**: 0.456
- **K-run variance**: 0.0063
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.235


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90164,"average_solve_count":122.0,"average_success_count":122.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05303,"approach_1.behind_distance_approach":0.11375,"descend_1.behind_distance_descend":0.0998,"push_1.push_distance":0.21956,"push_1.push_speed":0.12221},"optimized_scores":{"best_composite_score":0.45595,"best_fitness_score":0.76595,"best_task_score":0.91604},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":451.0,"contact_point_centroid":[0.46402,-0.06773,0.0469],"force_p95":19.23745,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.79569,"mean_force":5.38147,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.45564,-0.05637,0.0235]},{"body_a":"push_box","body_b":"link7","contact_count":21.0,"contact_point_centroid":[0.51694,-0.10643,0.05509],"force_p95":21.51984,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.63893,"mean_force":9.76963,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47905,-0.11068,0.02224]},{"body_a":"world","body_b":"push_box","contact_count":2084.0,"contact_point_centroid":[0.46397,-0.05825,-2e-05],"force_p95":9.80127,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.83283,"mean_force":1.6318,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.43064,0.00215,0.02496]},{"body_a":"world","body_b":"push_box","contact_count":2138.0,"contact_point_centroid":[0.51054,-0.14663,-2e-05],"force_p95":0.24555,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.41054,"mean_force":0.255,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.47892,-0.1105,0.06658]},{"body_a":"attachment","body_b":"push_box","contact_count":12.0,"contact_point_centroid":[0.49634,-0.12678,0.05134],"force_p95":0.92508,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.99892,"mean_force":0.41705,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48162,-0.11798,0.02264]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45787,0.03077,0.20276]},{"body_a":"world","body_b":"push_box","contact_count":1776.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.41225,0.06069,0.06849]}],"total_contact_groups":7},"final_pose_error":0.01188,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51032,-0.14689,0.02499],"final_tcp_position":[0.479,-0.11519,0.11103],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":28.79569,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_target","tcp_end":[0.41778,0.06157,0.10904],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12961,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":444.0,"n_steps_budget":600.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1776.0,"raw_peak_contact_force":0.24525,"subtask_id":"approach_target","tcp_end":[0.4088,0.06005,0.02897],"tcp_start":[0.41778,0.06157,0.10904],"tcp_to_object_dist_end":0.10066,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51131,-0.14556,0.02681],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.01228,"object_to_goal_dist_start":0.12843,"object_z_max":0.02785,"peak_contact_force":0.91231,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2556.0,"raw_peak_contact_force":28.79569,"subtask_id":"push_goal","tcp_end":[0.48227,-0.11804,0.02209],"tcp_start":[0.4088,0.06005,0.02897],"tcp_to_object_dist_end":0.04028,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":549.0,"n_steps_budget":630.0,"object_pos_end":[0.51032,-0.14689,0.02499],"object_pos_start":[0.51131,-0.14556,0.02681],"object_to_goal_dist_end":0.01078,"object_to_goal_dist_start":0.01228,"object_z_max":0.02681,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2150.0,"raw_peak_contact_force":2.41054,"tcp_end":[0.479,-0.11519,0.11103],"tcp_start":[0.48227,-0.11804,0.02209],"tcp_to_object_dist_end":0.09689,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.9,"average_solve_count":120.0,"average_success_count":120.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.04066,"approach_1.behind_distance_approach":0.10011,"descend_1.behind_distance_descend":0.05638,"push_1.push_distance":0.1859,"push_1.push_speed":0.11195},"optimized_scores":{"best_composite_score":0.52268,"best_fitness_score":0.83268,"best_task_score":0.96129},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.50427,-0.13023,0.02034],"force_p95":29.49306,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.97045,"mean_force":16.1966,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50543,-0.11832,0.02007]},{"body_a":"attachment","body_b":"push_box","contact_count":747.0,"contact_point_centroid":[0.52976,-0.05191,0.02036],"force_p95":15.78625,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.78248,"mean_force":3.88476,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53103,-0.04006,0.01992]},{"body_a":"world","body_b":"push_box","contact_count":2174.0,"contact_point_centroid":[0.50024,-0.15636,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.48845,"mean_force":0.26274,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50196,-0.11081,0.06347]},{"body_a":"world","body_b":"push_box","contact_count":1945.0,"contact_point_centroid":[0.53097,-0.0635,-4e-05],"force_p95":6.30965,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.07403,"mean_force":1.77142,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5375,-0.02134,0.02031]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52375,0.02911,0.2238]},{"body_a":"world","body_b":"push_box","contact_count":2908.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.55672,0.05622,0.08475]}],"total_contact_groups":6},"final_pose_error":0.01232,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50039,-0.1562,0.02499],"final_tcp_position":[0.50205,-0.11542,0.10859],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":30.97045,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_target","tcp_end":[0.54978,0.05854,0.15038],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13786,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":727.0,"n_steps_budget":810.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2908.0,"raw_peak_contact_force":0.24525,"subtask_id":"approach_target","tcp_end":[0.56618,0.05424,0.02532],"tcp_start":[0.54978,0.05854,0.15038],"tcp_to_object_dist_end":0.05446,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5009,-0.1549,0.02498],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.00499,"object_to_goal_dist_start":0.16043,"object_z_max":0.0255,"peak_contact_force":0.54685,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2692.0,"raw_peak_contact_force":25.78248,"subtask_id":"push_goal","tcp_end":[0.50546,-0.11827,0.02008],"tcp_start":[0.56618,0.05424,0.02532],"tcp_to_object_dist_end":0.03724,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":550.0,"n_steps_budget":630.0,"object_pos_end":[0.50039,-0.1562,0.02499],"object_pos_start":[0.5009,-0.1549,0.02498],"object_to_goal_dist_end":0.00621,"object_to_goal_dist_start":0.00499,"object_z_max":0.02503,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2176.0,"raw_peak_contact_force":30.97045,"tcp_end":[0.50205,-0.11542,0.10859],"tcp_start":[0.50546,-0.11827,0.02008],"tcp_to_object_dist_end":0.09303,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.18033,"average_solve_count":122.0,"average_success_count":122.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.04359,"approach_1.behind_distance_approach":0.10698,"descend_1.behind_distance_descend":0.09301,"push_1.push_distance":0.26998,"push_1.push_speed":0.15964},"optimized_scores":{"best_composite_score":0.33128,"best_fitness_score":0.64128,"best_task_score":0.75215},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":311.0,"contact_point_centroid":[0.54727,-0.07412,0.05465],"force_p95":42.15312,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":52.16595,"mean_force":24.54191,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51039,-0.07109,0.02152]},{"body_a":"world","body_b":"push_box","contact_count":1904.0,"contact_point_centroid":[0.54338,-0.02194,-5e-05],"force_p95":32.98313,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":47.27767,"mean_force":6.79602,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52858,0.03164,0.0207]},{"body_a":"attachment","body_b":"push_box","contact_count":641.0,"contact_point_centroid":[0.52954,-0.03275,0.04471],"force_p95":30.79377,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.3334,"mean_force":9.41954,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51832,-0.02419,0.02071]},{"body_a":"world","body_b":"push_box","contact_count":2208.0,"contact_point_centroid":[0.54599,-0.13931,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.36324,"mean_force":0.24523,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49647,-0.11747,0.06345]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51425,0.0416,0.22736]},{"body_a":"world","body_b":"push_box","contact_count":3328.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53846,0.10417,0.08913]}],"total_contact_groups":6},"final_pose_error":0.01225,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.54599,-0.13931,0.02499],"final_tcp_position":[0.49654,-0.12194,0.10922],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":52.16595,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_target","tcp_end":[0.53067,0.08367,0.15757],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.1407,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":832.0,"n_steps_budget":900.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3328.0,"raw_peak_contact_force":0.24525,"subtask_id":"approach_target","tcp_end":[0.54898,0.12515,0.02513],"tcp_start":[0.53067,0.08367,0.15757],"tcp_to_object_dist_end":0.08907,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54542,-0.13916,0.02448],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.0467,"object_to_goal_dist_start":0.1905,"object_z_max":0.02955,"peak_contact_force":0.38901,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2856.0,"raw_peak_contact_force":52.16595,"subtask_id":"push_goal","tcp_end":[0.49992,-0.12483,0.02063],"tcp_start":[0.54898,0.12515,0.02513],"tcp_to_object_dist_end":0.04786,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":552.0,"n_steps_budget":630.0,"object_pos_end":[0.54599,-0.13931,0.02499],"object_pos_start":[0.54542,-0.13916,0.02448],"object_to_goal_dist_end":0.04722,"object_to_goal_dist_start":0.0467,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2208.0,"raw_peak_contact_force":0.36324,"tcp_end":[0.49654,-0.12194,0.10922],"tcp_start":[0.49992,-0.12483,0.02063],"tcp_to_object_dist_end":0.09921,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```