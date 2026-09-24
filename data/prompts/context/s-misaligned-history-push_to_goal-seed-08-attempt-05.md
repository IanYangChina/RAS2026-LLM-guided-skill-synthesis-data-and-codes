## Search State

- **Seed**: 8
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 8  | 0.5079 | 0.45 | ❌ rejected |
| 4 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 7  | 0.2367 | 0.47 | ❌ rejected |
| 3 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 6  | 0.4257 | 0.78 | ✅ accepted |
| 2 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 6  | -0.3100 | 0.00 | ❌ rejected |
| 1 | pull → insert → descend → contact | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_control | impedance_control | position_control | impedance_control | time_limit | pose_tolerance | contact_detected | force_exceeded | 5  | 0.2515 | 0.72 | ❌ rejected |

**Proposal policy**: task_score is 0.72 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.779, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.251) — your mutation base

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

- **Composite score**: 0.251
- **task_score** (E): 0.717
- **fitness_score**: 0.681  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.430

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above_behind | 1.00 | 1.00 | 0.2271 |
| descend_to_contact_side | 1.00 | 1.00 | 0.0522 |
| push_to_goal | 1.00 | 1.00 | 0.1904 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above_behind | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.529, 0.038, 0.086) | (0.526, -0.001, 0.025)→(0.526, -0.001, 0.025) | 0.156→0.156 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_to_contact_side | descend | 1.00 / step_budget | (0.529, 0.038, 0.086)→(0.535, 0.027, 0.037) | (0.526, -0.001, 0.025)→(0.526, -0.008, 0.027) | 0.156→0.149 | 1.00 / 2.667 | 72.988 | 201.855 |
| push_to_goal | push | 1.00 / step_budget | (0.535, 0.027, 0.037)→(0.496, -0.152, 0.029) | (0.526, -0.008, 0.027)→(0.515, -0.158, 0.027) | 0.149→0.040 | 1.00 / 2.333 | 1.326 | 105.066 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.728
- goal_progress: 0.865
- terminal_score: 0.865
- phase_score: 0.654
- phase_breakdown.push_goal_score: 0.789
- phase_breakdown.approach_tcp_score: 0.340

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.739
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.865
- **Median Q (composite search score)**: 0.302
- **K-run variance**: 0.0058
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.370


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.42424,"average_solve_count":66.0,"average_success_count":66.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_behind.approach_height":0.05552,"approach_above_behind.approach_speed":0.2523,"approach_above_behind.lateral_behind_distance":-0.0363,"descend_to_contact_side.descend_speed":0.1042,"descend_to_contact_side.lateral_behind_distance":-0.03416,"push_to_goal.push_distance":0.27405,"push_to_goal.push_pose_tolerance":0.04016,"push_to_goal.push_speed":0.23608},"optimized_scores":{"best_composite_score":0.30873,"best_fitness_score":0.73873,"best_task_score":0.86535},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":46.0,"contact_point_centroid":[0.47626,0.08281,0.04667],"force_p95":145.18427,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":159.01539,"mean_force":85.61369,"phase_index":1.0,"phase_name":"descend_to_contact_side","phase_type":"descend","tcp_position_centroid":[0.4727,0.09319,0.04791]},{"body_a":"push_box","body_b":"link7","contact_count":43.0,"contact_point_centroid":[0.5281,-0.07585,0.05441],"force_p95":107.0122,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":110.81951,"mean_force":27.04643,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48681,-0.06353,0.02995]},{"body_a":"attachment","body_b":"push_box","contact_count":145.0,"contact_point_centroid":[0.48954,-0.01532,0.04405],"force_p95":44.5103,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":100.58955,"mean_force":7.94413,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48069,-0.00398,0.03057]},{"body_a":"world","body_b":"push_box","contact_count":797.0,"contact_point_centroid":[0.47932,0.05739,-5e-05],"force_p95":34.39742,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":99.78366,"mean_force":5.20361,"phase_index":1.0,"phase_name":"descend_to_contact_side","phase_type":"descend","tcp_position_centroid":[0.47231,0.09274,0.06255]},{"body_a":"world","body_b":"push_box","contact_count":197.0,"contact_point_centroid":[0.50431,-0.08266,-0.00021],"force_p95":60.3752,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":92.6898,"mean_force":12.10868,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48369,-0.03369,0.03032]},{"body_a":"world","body_b":"push_box","contact_count":2328.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_above_behind","phase_type":"approach","tcp_position_centroid":[0.48722,0.05729,0.20228]}],"total_contact_groups":6},"final_pose_error":0.03947,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50711,-0.17674,0.03048],"final_tcp_position":[0.49461,-0.14049,0.02956],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":159.01539,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":582.0,"n_steps_budget":630.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_above_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2328.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_tcp","tcp_end":[0.47385,0.09279,0.09112],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0747,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":205.0,"n_steps_budget":600.0,"object_pos_end":[0.47931,0.05647,0.025],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2075,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.48492,"phase_name":"descend_to_contact_side","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":843.0,"raw_peak_contact_force":159.01539,"subtask_id":"approach_tcp","tcp_end":[0.47271,0.09339,0.03439],"tcp_start":[0.47385,0.09279,0.09112],"tcp_to_object_dist_end":0.03867,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":277.0,"n_steps_budget":750.0,"object_pos_end":[0.50711,-0.17674,0.03048],"object_pos_start":[0.47931,0.05647,0.025],"object_to_goal_dist_end":0.02821,"object_to_goal_dist_start":0.2075,"object_z_max":0.03074,"peak_contact_force":0.25631,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":385.0,"raw_peak_contact_force":110.81951,"subtask_id":"push_goal","tcp_end":[0.49461,-0.14049,0.02956],"tcp_start":[0.47271,0.09339,0.03439],"tcp_to_object_dist_end":0.03836,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.47541,"average_solve_count":61.0,"average_success_count":61.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_behind.approach_height":0.0549,"approach_above_behind.approach_speed":0.26204,"approach_above_behind.lateral_behind_distance":-0.04501,"descend_to_contact_side.descend_speed":0.2086,"descend_to_contact_side.lateral_behind_distance":-0.02095,"push_to_goal.push_distance":0.20533,"push_to_goal.push_pose_tolerance":0.04965,"push_to_goal.push_speed":0.21151},"optimized_scores":{"best_composite_score":0.30153,"best_fitness_score":0.73153,"best_task_score":0.6901},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":123.0,"contact_point_centroid":[0.56196,-0.00174,0.04671],"force_p95":225.61964,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":229.30262,"mean_force":171.58921,"phase_index":1.0,"phase_name":"descend_to_contact_side","phase_type":"descend","tcp_position_centroid":[0.55412,0.00641,0.0477]},{"body_a":"world","body_b":"push_box","contact_count":877.0,"contact_point_centroid":[0.54758,-0.02358,-0.00023],"force_p95":137.4927,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":182.64804,"mean_force":24.64664,"phase_index":1.0,"phase_name":"descend_to_contact_side","phase_type":"descend","tcp_position_centroid":[0.55154,0.01067,0.05987]},{"body_a":"attachment","body_b":"push_box","contact_count":57.0,"contact_point_centroid":[0.53844,-0.06647,0.04016],"force_p95":15.57644,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":51.66252,"mean_force":4.94959,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.53249,-0.05565,0.02681]},{"body_a":"world","body_b":"push_box","contact_count":117.0,"contact_point_centroid":[0.52303,-0.1068,-0.00028],"force_p95":16.74784,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":49.53323,"mean_force":4.02995,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.53047,-0.06224,0.02696]},{"body_a":"push_box","body_b":"link7","contact_count":17.0,"contact_point_centroid":[0.54346,-0.13856,0.05488],"force_p95":29.92354,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.27135,"mean_force":6.71327,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.51241,-0.11487,0.02379]},{"body_a":"world","body_b":"push_box","contact_count":2208.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_above_behind","phase_type":"approach","tcp_position_centroid":[0.52419,0.02246,0.19688]}],"total_contact_groups":6},"final_pose_error":0.04885,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50899,-0.18994,0.02503],"final_tcp_position":[0.50129,-0.14748,0.02258],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":229.30262,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":552.0,"n_steps_budget":600.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_above_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2208.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_tcp","tcp_end":[0.55183,0.02049,0.08854],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07884,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":277.0,"n_steps_budget":600.0,"object_pos_end":[0.5364,-0.04257,0.02833],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.11348,"object_to_goal_dist_start":0.13211,"object_z_max":0.03002,"peak_contact_force":1.23133,"phase_name":"descend_to_contact_side","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1000.0,"raw_peak_contact_force":229.30262,"subtask_id":"approach_tcp","tcp_end":[0.55329,0.00025,0.03262],"tcp_start":[0.55183,0.02049,0.08854],"tcp_to_object_dist_end":0.04622,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":149.0,"n_steps_budget":630.0,"object_pos_end":[0.50899,-0.18994,0.02503],"object_pos_start":[0.5364,-0.04257,0.02833],"object_to_goal_dist_end":0.04094,"object_to_goal_dist_start":0.11348,"object_z_max":0.03047,"peak_contact_force":3.48107,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":191.0,"raw_peak_contact_force":51.66252,"subtask_id":"push_goal","tcp_end":[0.50129,-0.14748,0.02258],"tcp_start":[0.55329,0.00025,0.03262],"tcp_to_object_dist_end":0.04323,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.12329,"average_solve_count":73.0,"average_success_count":73.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_behind.approach_height":0.04685,"approach_above_behind.approach_speed":0.21308,"approach_above_behind.lateral_behind_distance":-0.03599,"descend_to_contact_side.descend_speed":0.2248,"descend_to_contact_side.lateral_behind_distance":-0.01992,"push_to_goal.push_distance":0.20236,"push_to_goal.push_pose_tolerance":0.02369,"push_to_goal.push_speed":0.14904},"optimized_scores":{"best_composite_score":0.1441,"best_fitness_score":0.5741,"best_task_score":0.59466},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":200.0,"contact_point_centroid":[0.57937,-0.01311,0.04593],"force_p95":207.51289,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":217.24719,"mean_force":174.01775,"phase_index":1.0,"phase_name":"descend_to_contact_side","phase_type":"descend","tcp_position_centroid":[0.56905,-0.0087,0.04718]},{"body_a":"world","body_b":"push_box","contact_count":791.0,"contact_point_centroid":[0.56616,-0.03504,-0.00042],"force_p95":177.47151,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":187.09258,"mean_force":44.60715,"phase_index":1.0,"phase_name":"descend_to_contact_side","phase_type":"descend","tcp_position_centroid":[0.56496,-0.00543,0.05534]},{"body_a":"attachment","body_b":"push_box","contact_count":407.0,"contact_point_centroid":[0.56708,-0.05493,0.04833],"force_p95":151.00902,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":152.71453,"mean_force":127.37366,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.55794,-0.06,0.04985]},{"body_a":"world","body_b":"push_box","contact_count":1209.0,"contact_point_centroid":[0.54854,-0.07135,-0.00048],"force_p95":88.73622,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":99.95393,"mean_force":43.31853,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.54852,-0.07427,0.04747]},{"body_a":"world","body_b":"push_box","contact_count":2660.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_above_behind","phase_type":"approach","tcp_position_centroid":[0.53004,0.01462,0.1891]}],"total_contact_groups":5},"final_pose_error":0.02368,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52911,-0.10741,0.02479],"final_tcp_position":[0.49074,-0.16848,0.0359],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":217.24719,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":665.0,"n_steps_budget":720.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_above_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2660.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_tcp","tcp_end":[0.56257,0.00189,0.078],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.06511,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":285.0,"n_steps_budget":600.0,"object_pos_end":[0.56124,-0.03855,0.02794],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.1272,"object_to_goal_dist_start":0.12728,"object_z_max":0.02803,"peak_contact_force":217.24719,"phase_name":"descend_to_contact_side","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":991.0,"raw_peak_contact_force":217.24719,"subtask_id":"approach_tcp","tcp_end":[0.57931,-0.0128,0.04445],"tcp_start":[0.56257,0.00189,0.078],"tcp_to_object_dist_end":0.03553,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":510.0,"n_steps_budget":870.0,"object_pos_end":[0.52911,-0.10741,0.02479],"object_pos_start":[0.56124,-0.03855,0.02794],"object_to_goal_dist_end":0.05159,"object_to_goal_dist_start":0.1272,"object_z_max":0.03524,"peak_contact_force":0.23947,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1616.0,"raw_peak_contact_force":152.71453,"subtask_id":"push_goal","tcp_end":[0.49074,-0.16848,0.0359],"tcp_start":[0.57931,-0.0128,0.04445],"tcp_to_object_dist_end":0.07298,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```