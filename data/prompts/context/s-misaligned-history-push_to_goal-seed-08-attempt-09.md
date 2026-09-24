## Search State

- **Seed**: 8
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 6  | 0.3738 | 0.64 | ❌ rejected |
| 8 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 6  | 0.4396 | 0.81 | ✅ accepted |
| 7 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 6  | 0.5647 | 0.56 | ❌ rejected |
| 6 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 6  | 0.2515 | 0.72 | ❌ rejected |
| 5 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 8  | 0.5405 | 0.43 | ❌ rejected |

**Proposal policy**: task_score is 0.43 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`
- Frozen object start: [0.4792366731926673, 0.05847322120055107, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.4792366731926673, 0.05847322120055107, 0.025)
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
  frozen_object_start: [0.4792, 0.0585, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.4792366731926673, 0.05847322120055107, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [0.0208, -0.2085, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.808, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.4792366731926673, 0.05847322120055107, 0.025) | approach/contact targets near object start |
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

## Current Skill (Q=0.541) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: approach_tcp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.3
- id: push_goal
  target_entity: object
  weight: 0.7
phases:
- id: approach_over_object
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
    - 0.05
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_tcp
- id: descend_to_contact
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.025
    offset_along_axis:
      distance: -0.02
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: positive
  parameters:
    descend_force_threshold:
      type: scalar
      range:
      - 1.0
      - 10.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    descend_lateral_offset:
      type: scalar
      range:
      - -0.05
      - -0.005
      default: -0.02
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  subtask_id: approach_tcp
- id: push_to_goal
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.25
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.4
      default: 0.25
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_pose_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: push_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_over_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.05]
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_contact** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.025], offset_along_axis={axis=task_goal_direction, distance=-0.02, mode=replace_offset_projection, sign=positive}
  - parameter_bindings:
    - descend_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - descend_lateral_offset: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **push_to_goal** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.25, mode=add_to_offset, sign=positive}
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_pose_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)

## Design Metrics

- **Composite score**: 0.541
- **task_score** (E): 0.430
- **fitness_score**: 0.537  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_over_object | 1.00 | 1.00 | 0.2017 |
| descend_to_contact | 1.00 | 1.00 | 0.0522 |
| push_to_goal | 1.00 | 1.00 | 0.1563 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_over_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.521, 0.004, 0.107) | (0.526, -0.001, 0.025)→(0.526, -0.001, 0.025) | 0.156→0.156 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_to_contact | descend | 1.00 / force_exceeded | (0.521, 0.004, 0.107)→(0.520, 0.001, 0.054) | (0.526, -0.001, 0.025)→(0.526, -0.001, 0.025) | 0.156→0.156 | 1.00 / 5.000 | 50608.876 | 0.245 |
| push_to_goal | push | 1.00 / step_budget | (0.520, 0.001, 0.054)→(0.491, -0.148, 0.050) | (0.526, -0.001, 0.025)→(0.513, -0.061, 0.025) | 0.156→0.094 | 1.00 / 4.000 | 0.254 | 124.970 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.529
- lateral_force_integral: None
- approach_alignment: 0.732
- goal_progress: 0.527
- terminal_score: 0.527
- phase_score: 0.606
- phase_breakdown.push_goal_score: 0.592
- phase_breakdown.approach_tcp_score: 0.637

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.574
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.527
- **Median Q (composite search score)**: 0.568
- **K-run variance**: 0.0021
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.289


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `8267fcc1127ab3c529e380fe6aea430def9956719b146bd9818eb52355cb895d`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `33d626702a3717cebb1eda35e1cb80c1c9d108c246efccd193577b9105813420`; realized-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47924,0.05847,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02076,-0.20847,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47924,0.05847,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0101,"average_solve_count":99.0,"average_success_count":99.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_over_object.approach_height":0.06212,"approach_over_object.approach_speed":0.1616,"descend_to_contact.descend_force_threshold":3.49813,"descend_to_contact.descend_speed":0.05078,"push_to_goal.push_distance":0.24955,"push_to_goal.push_pose_tolerance":0.04114},"optimized_scores":{"best_composite_score":0.47658,"best_fitness_score":0.47324,"best_task_score":0.26122},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":83.0,"contact_point_centroid":[0.48627,0.04036,0.05267],"force_p95":165.19841,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":169.06669,"mean_force":109.81741,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.47811,0.03422,0.05637]},{"body_a":"world","body_b":"push_box","contact_count":714.0,"contact_point_centroid":[0.48275,0.01049,-0.00027],"force_p95":126.02389,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":147.70335,"mean_force":13.20965,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48526,-0.06241,0.05237]},{"body_a":"world","body_b":"push_box","contact_count":2504.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_over_object","phase_type":"approach","tcp_position_centroid":[0.48845,0.04059,0.20304]},{"body_a":"world","body_b":"push_box","contact_count":968.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.47464,0.05848,0.07533]}],"total_contact_groups":4},"final_pose_error":0.04082,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48268,0.0038,0.02499],"final_tcp_position":[0.49282,-0.15008,0.05031],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":169.06669,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":626.0,"n_steps_budget":870.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_over_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2504.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_tcp","tcp_end":[0.47718,0.05901,0.09671],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07176,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":242.0,"n_steps_budget":900.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":39.55438,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":968.0,"raw_peak_contact_force":0.24525,"subtask_id":"approach_tcp","tcp_end":[0.47436,0.05825,0.05558],"tcp_start":[0.47718,0.05901,0.09671],"tcp_to_object_dist_end":0.03098,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":266.0,"n_steps_budget":1000.0,"object_pos_end":[0.48268,0.0038,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.15478,"object_to_goal_dist_start":0.2095,"object_z_max":0.03519,"peak_contact_force":0.24523,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":797.0,"raw_peak_contact_force":169.06669,"subtask_id":"push_goal","tcp_end":[0.49282,-0.15008,0.05031],"tcp_start":[0.47436,0.05825,0.05558],"tcp_to_object_dist_end":0.15629,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `021f3e69028f16fb65e79b302b37775f7324e143e034cbac30fdb04ffcd99d24`; realized-scene SHA-256: `2cf7387f3e8baf02f18930263090d6f78777bdbc147b7fa30c178332e76b547b`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54443,-0.02558,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.04443,-0.12442,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.54443,-0.02558,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.65882,"average_solve_count":85.0,"average_success_count":85.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_over_object.approach_height":0.07748,"approach_over_object.approach_speed":0.13538,"descend_to_contact.descend_force_threshold":1.41672,"descend_to_contact.descend_speed":0.05686,"push_to_goal.push_distance":0.15169,"push_to_goal.push_pose_tolerance":0.01962},"optimized_scores":{"best_composite_score":0.56753,"best_fitness_score":0.5642,"best_task_score":0.50256},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":217.0,"contact_point_centroid":[0.5351,-0.0512,0.05252],"force_p95":94.27155,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":95.31261,"mean_force":63.06634,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.52646,-0.05777,0.05487]},{"body_a":"world","body_b":"push_box","contact_count":769.0,"contact_point_centroid":[0.53255,-0.06744,-0.00025],"force_p95":72.71503,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":83.8484,"mean_force":18.25567,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.51319,-0.08879,0.0523]},{"body_a":"world","body_b":"push_box","contact_count":2572.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_over_object","phase_type":"approach","tcp_position_centroid":[0.51845,0.00154,0.202]},{"body_a":"world","body_b":"push_box","contact_count":1248.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.53671,-0.02158,0.07938]}],"total_contact_groups":4},"final_pose_error":0.01928,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52521,-0.08931,0.02497],"final_tcp_position":[0.48944,-0.14761,0.04911],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":643.0,"n_steps_budget":960.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_over_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2572.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_tcp","tcp_end":[0.53832,-0.01995,0.10786],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08329,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":312.0,"n_steps_budget":930.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1248.0,"raw_peak_contact_force":0.24525,"subtask_id":"approach_tcp","tcp_end":[0.53765,-0.02317,0.05406],"tcp_start":[0.53832,-0.01995,0.10786],"tcp_to_object_dist_end":0.02995,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":346.0,"n_steps_budget":960.0,"object_pos_end":[0.52521,-0.08931,0.02497],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.06572,"object_to_goal_dist_start":0.13211,"object_z_max":0.0354,"peak_contact_force":0.24541,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":986.0,"raw_peak_contact_force":95.31261,"subtask_id":"push_goal","tcp_end":[0.48944,-0.14761,0.04911],"tcp_start":[0.53765,-0.02317,0.05406],"tcp_to_object_dist_end":0.07254,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `886824c4c8b8334954c1de9b3100fb0acfdd4a04855e7e82a07b72c52723cc86`; realized-scene SHA-256: `d6f67641a3df0efca2ae6de2763dea57e4736e336d1ca3e6fe373ea0745d2d85`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.55472,-0.03508,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.05472,-0.11492,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.55472,-0.03508,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.80769,"average_solve_count":78.0,"average_success_count":78.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_over_object.approach_height":0.08413,"approach_over_object.approach_speed":0.21834,"descend_to_contact.descend_force_threshold":2.42174,"descend_to_contact.descend_speed":0.05287,"push_to_goal.push_distance":0.15343,"push_to_goal.push_pose_tolerance":0.02828},"optimized_scores":{"best_composite_score":0.57743,"best_fitness_score":0.5741,"best_task_score":0.52682},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":154.0,"contact_point_centroid":[0.54257,-0.05917,0.05283],"force_p95":107.95406,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":110.53087,"mean_force":73.4357,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.53388,-0.06569,0.05525]},{"body_a":"world","body_b":"push_box","contact_count":405.0,"contact_point_centroid":[0.5397,-0.07378,-0.00043],"force_p95":94.7438,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":106.25212,"mean_force":28.54026,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.52287,-0.08523,0.05314]},{"body_a":"world","body_b":"push_box","contact_count":2184.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_over_object","phase_type":"approach","tcp_position_centroid":[0.52319,-0.00287,0.20604]},{"body_a":"world","body_b":"push_box","contact_count":1424.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.54653,-0.03043,0.08242]}],"total_contact_groups":4},"final_pose_error":0.02772,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52962,-0.09756,0.0246],"final_tcp_position":[0.49143,-0.14527,0.04929],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":546.0,"n_steps_budget":600.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_over_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2184.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_tcp","tcp_end":[0.54788,-0.0284,0.11508],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.09059,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":356.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1424.0,"raw_peak_contact_force":0.24525,"subtask_id":"approach_tcp","tcp_end":[0.5479,-0.03241,0.05365],"tcp_start":[0.54788,-0.0284,0.11508],"tcp_to_object_dist_end":0.02959,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":233.0,"n_steps_budget":960.0,"object_pos_end":[0.52962,-0.09756,0.0246],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.06023,"object_to_goal_dist_start":0.12728,"object_z_max":0.03776,"peak_contact_force":0.27265,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":559.0,"raw_peak_contact_force":110.53087,"subtask_id":"push_goal","tcp_end":[0.49143,-0.14527,0.04929],"tcp_start":[0.5479,-0.03241,0.05365],"tcp_to_object_dist_end":0.06591,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```