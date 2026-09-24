## Search State

- **Seed**: 8
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 6  | 0.5405 | 0.43 | ❌ rejected |
| 9 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 6  | 0.3738 | 0.64 | ❌ rejected |
| 8 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 6  | 0.4396 | 0.81 | ✅ accepted |
| 7 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 6  | 0.5647 | 0.56 | ❌ rejected |
| 6 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 6  | 0.3349 | 0.81 | ✅ accepted |

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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.814, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.335) — your mutation base

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

- **Composite score**: 0.335
- **task_score** (E): 0.814
- **fitness_score**: 0.665  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_over_object | 1.00 | 1.00 | 0.1986 |
| descend_to_contact | 0.00 | 1.00 | 0.0738 |
| push_to_goal | 1.00 | 1.00 | 0.1949 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_over_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.521, 0.003, 0.110) | (0.526, -0.001, 0.025)→(0.526, -0.001, 0.025) | 0.156→0.156 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_to_contact | descend | 0.00 / step_budget | (0.521, 0.003, 0.110)→(0.532, 0.041, 0.049) | (0.526, -0.001, 0.025)→(0.526, -0.001, 0.025) | 0.156→0.156 | 1.00 / 4.000 | 0.245 | 0.245 |
| push_to_goal | push | 1.00 / step_budget | (0.532, 0.041, 0.049)→(0.496, -0.144, 0.043) | (0.526, -0.001, 0.025)→(0.521, -0.155, 0.030) | 0.156→0.028 | 1.00 / 1.333 | 0.493 | 82.997 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.940
- lateral_force_integral: None
- approach_alignment: 0.757
- goal_progress: 0.851
- terminal_score: 0.851
- phase_score: 0.570
- phase_breakdown.push_goal_score: 0.656
- phase_breakdown.approach_tcp_score: 0.369

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.682
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.851
- **Median Q (composite search score)**: 0.328
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.312


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.12381,"average_solve_count":105.0,"average_success_count":105.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_over_object.approach_height":0.08013,"approach_over_object.approach_speed":0.19008,"descend_to_contact.descend_force_threshold":3.70357,"descend_to_contact.descend_lateral_offset":-0.04647,"push_to_goal.push_distance":0.30011,"push_to_goal.push_pose_tolerance":0.04357},"optimized_scores":{"best_composite_score":0.35248,"best_fitness_score":0.68248,"best_task_score":0.85149},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":132.0,"contact_point_centroid":[0.48773,-0.02633,0.0471],"force_p95":105.09165,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":112.33606,"mean_force":19.05868,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48111,-0.01853,0.04603]},{"body_a":"world","body_b":"push_box","contact_count":281.0,"contact_point_centroid":[0.50949,-0.04279,-0.00017],"force_p95":65.82726,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":100.70998,"mean_force":9.79164,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48061,-0.0116,0.04655]},{"body_a":"world","body_b":"push_box","contact_count":2220.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_over_object","phase_type":"approach","tcp_position_centroid":[0.48866,0.03923,0.21185]},{"body_a":"world","body_b":"push_box","contact_count":2100.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.47276,0.07959,0.08033]}],"total_contact_groups":4},"final_pose_error":0.04353,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52579,-0.1329,0.02819],"final_tcp_position":[0.49416,-0.15522,0.04459],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":112.33606,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":555.0,"n_steps_budget":690.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_over_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2220.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_tcp","tcp_end":[0.47747,0.0586,0.11486],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08989,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":525.0,"n_steps_budget":600.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2100.0,"raw_peak_contact_force":0.24525,"subtask_id":"approach_tcp","tcp_end":[0.47088,0.1007,0.04995],"tcp_start":[0.47747,0.0586,0.11486],"tcp_to_object_dist_end":0.04976,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":304.0,"n_steps_budget":1000.0,"object_pos_end":[0.52579,-0.1329,0.02819],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.03111,"object_to_goal_dist_start":0.2095,"object_z_max":0.03688,"peak_contact_force":1.13428,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":413.0,"raw_peak_contact_force":112.33606,"subtask_id":"push_goal","tcp_end":[0.49416,-0.15522,0.04459],"tcp_start":[0.47088,0.1007,0.04995],"tcp_to_object_dist_end":0.04204,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0,"average_solve_count":80.0,"average_success_count":80.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_over_object.approach_height":0.05957,"approach_over_object.approach_speed":0.29843,"descend_to_contact.descend_force_threshold":7.90863,"descend_to_contact.descend_lateral_offset":-0.04741,"push_to_goal.push_distance":0.19426,"push_to_goal.push_pose_tolerance":0.03233},"optimized_scores":{"best_composite_score":0.32445,"best_fitness_score":0.65445,"best_task_score":0.79718},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":98.0,"contact_point_centroid":[0.52666,-0.07586,0.0454],"force_p95":44.70746,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":62.05216,"mean_force":7.49414,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.52258,-0.06471,0.0428]},{"body_a":"world","body_b":"push_box","contact_count":231.0,"contact_point_centroid":[0.53786,-0.09033,-8e-05],"force_p95":22.2426,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":38.47289,"mean_force":3.8544,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.53082,-0.04314,0.04372]},{"body_a":"world","body_b":"push_box","contact_count":2200.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_over_object","phase_type":"approach","tcp_position_centroid":[0.51798,0.00286,0.19603]},{"body_a":"world","body_b":"push_box","contact_count":2108.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.54459,-0.00157,0.06752]}],"total_contact_groups":4},"final_pose_error":0.03172,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52405,-0.15948,0.03205],"final_tcp_position":[0.49649,-0.13658,0.04205],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":62.05216,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":550.0,"n_steps_budget":600.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_over_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2200.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_tcp","tcp_end":[0.53799,-0.0191,0.0924],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.06802,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":527.0,"n_steps_budget":600.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2108.0,"raw_peak_contact_force":0.24525,"subtask_id":"approach_tcp","tcp_end":[0.55431,0.01599,0.04728],"tcp_start":[0.53799,-0.0191,0.0924],"tcp_to_object_dist_end":0.0482,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":245.0,"n_steps_budget":1000.0,"object_pos_end":[0.52405,-0.15948,0.03205],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.02679,"object_to_goal_dist_start":0.13211,"object_z_max":0.03213,"peak_contact_force":0.17706,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":329.0,"raw_peak_contact_force":62.05216,"subtask_id":"push_goal","tcp_end":[0.49649,-0.13658,0.04205],"tcp_start":[0.55431,0.01599,0.04728],"tcp_to_object_dist_end":0.0372,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.15476,"average_solve_count":84.0,"average_success_count":84.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_over_object.approach_height":0.09303,"approach_over_object.approach_speed":0.17988,"descend_to_contact.descend_force_threshold":5.17975,"descend_to_contact.descend_lateral_offset":-0.04878,"push_to_goal.push_distance":0.19806,"push_to_goal.push_pose_tolerance":0.0347},"optimized_scores":{"best_composite_score":0.32788,"best_fitness_score":0.65788,"best_task_score":0.79306},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":100.0,"contact_point_centroid":[0.53312,-0.07624,0.04556],"force_p95":66.34678,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":74.60221,"mean_force":10.45268,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.53272,-0.06481,0.04455]},{"body_a":"world","body_b":"push_box","contact_count":246.0,"contact_point_centroid":[0.53481,-0.09889,-9e-05],"force_p95":24.67605,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":51.14906,"mean_force":4.81266,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.53885,-0.05278,0.04516]},{"body_a":"world","body_b":"push_box","contact_count":2284.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_over_object","phase_type":"approach","tcp_position_centroid":[0.52375,-0.00378,0.20836]},{"body_a":"world","body_b":"push_box","contact_count":2152.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.55717,-0.01168,0.0837]}],"total_contact_groups":4},"final_pose_error":0.03419,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51379,-0.17217,0.02849],"final_tcp_position":[0.49606,-0.14103,0.04363],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":74.60221,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":571.0,"n_steps_budget":690.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_over_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2284.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_tcp","tcp_end":[0.54816,-0.02908,0.12239],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.09781,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":538.0,"n_steps_budget":600.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2152.0,"raw_peak_contact_force":0.24525,"subtask_id":"approach_tcp","tcp_end":[0.56935,0.00616,0.04889],"tcp_start":[0.54816,-0.02908,0.12239],"tcp_to_object_dist_end":0.04986,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":230.0,"n_steps_budget":1000.0,"object_pos_end":[0.51379,-0.17217,0.02849],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.02634,"object_to_goal_dist_start":0.12728,"object_z_max":0.02867,"peak_contact_force":0.16868,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":346.0,"raw_peak_contact_force":74.60221,"subtask_id":"push_goal","tcp_end":[0.49606,-0.14103,0.04363],"tcp_start":[0.56935,0.00616,0.04889],"tcp_to_object_dist_end":0.0389,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```