## Search State

- **Seed**: 0
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 12 | -0.5432 | 0.05 | ❌ rejected |
| 11 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.2145 | 0.40 | ❌ rejected |
| 10 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.0434 | 0.00 | ❌ rejected |
| 9 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.0690 | 0.51 | ❌ rejected |
| 8 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.0248 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.05 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `79fe20ee7316d80bc617c84166fccacf882b4f96b2faf4b155be83e4f318b183`
- Frozen object start: [0.5164354024785746, -0.027625594348335558, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5164354024785746, -0.027625594348335558, 0.025)
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
  frozen_object_start: [0.5164, -0.0276, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5164354024785746, -0.027625594348335558, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0164, -0.1224, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 79fe20ee7316d80bc617c84166fccacf882b4f96b2faf4b155be83e4f318b183

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.819, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.5164354024785746, -0.027625594348335558, 0.025) | approach/contact targets near object start |
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

## Current Skill (Q=-0.543) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: insert_1
  type: insert
  generator: linear_cartesian
  control: impedance_control
  termination: force_exceeded
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: insert_2
  type: insert
  generator: impedance_motion
  control: admittance_control
  termination: force_exceeded

```

## Design Metrics

- **Composite score**: -0.543
- **task_score** (E): 0.052
- **fitness_score**: 0.117  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.660

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1281 |
| descend_1 | 0.00 | 1.00 | 0.1033 |
| push_1 | 0.00 | 1.00 | 0.0004 |
| retract_1 | 1.00 | 1.00 | 0.1007 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.494, 0.001, 0.179) | (0.496, 0.001, 0.025)→(0.496, 0.001, 0.025) | 0.152→0.152 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_1 | descend | 0.00 / step_budget | (0.494, 0.001, 0.179)→(0.507, -0.021, 0.093) | (0.496, 0.001, 0.025)→(0.466, -0.004, 0.025) | 0.152→0.152 | 1.00 / 5.000 | 265.101 | 1019.053 |
| push_1 | push | 0.00 / guard_failure | (0.507, -0.022, 0.093)→(0.507, -0.022, 0.093) | (0.466, -0.004, 0.025)→(0.466, -0.004, 0.025) | 0.152→0.152 | 1.00 / 5.000 | 261.641 | 270.351 |
| retract_1 | retract | 1.00 / step_budget | (0.507, -0.022, 0.093)→(0.469, -0.006, 0.170) | (0.466, -0.004, 0.025)→(0.466, -0.004, 0.025) | 0.152→0.152 | 1.00 / 4.000 | 0.245 | 302.201 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.204
- lateral_force_integral: None
- approach_alignment: 0.654
- goal_progress: 0.079
- terminal_score: 0.079
- phase_score: 0.179
- phase_breakdown.push_to_goal_score: 0.135
- phase_breakdown.reach_object_score: 0.283

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.139
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.079
- **Median Q (composite search score)**: -0.547
- **K-run variance**: 0.0003
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.354


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `1efc9b29f7d131941a1bd842274a029ca5b2a2ff6a8656033ab118e32e2fae7d`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `6150c547b3cd2920ed4582689733d59ef61d18dc295ccd2a0d2317d1cf4e7764`; realized-scene SHA-256: `79fe20ee7316d80bc617c84166fccacf882b4f96b2faf4b155be83e4f318b183`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51644,-0.02763,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.01644,-0.12237,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.51644,-0.02763,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.34146,"average_solve_count":82.0,"average_success_count":82.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.23797,"approach_1.approach_tolerance":0.01085,"descend_1.descend_speed":0.02425,"descend_1.descend_tolerance":0.0124,"push_1.guard_force_threshold":13.33072,"push_1.push_distance":0.11525,"push_1.push_speed":0.05101,"push_1.push_tolerance":0.00915,"push_1.retry_lateral_x":-0.00271,"push_1.retry_lateral_y":0.00611,"retract_1.retract_height":0.12442,"retract_1.retract_speed":0.10375},"optimized_scores":{"best_composite_score":-0.521,"best_fitness_score":0.139,"best_task_score":0.07858},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"world","contact_count":31.0,"contact_point_centroid":[0.56632,-0.02083,-0.00294],"force_p95":950.72948,"geom_a":"pusher_tip","geom_b":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1031.08933,"mean_force":191.41588,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.55906,-0.0219,0.00357]},{"body_a":"world","body_b":"link6","contact_count":438.0,"contact_point_centroid":[0.66883,0.00425,-0.00015],"force_p95":288.75496,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":611.23362,"mean_force":241.62024,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51886,-0.09211,0.08668]},{"body_a":"world","body_b":"link7","contact_count":491.0,"contact_point_centroid":[0.62341,-0.05428,-0.00015],"force_p95":299.59235,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":498.96305,"mean_force":206.64527,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.55218,-0.05035,0.02981]},{"body_a":"world","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.67789,0.00388,-0.00012],"force_p95":253.7787,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":254.35917,"mean_force":248.52071,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51772,-0.08568,0.09969]},{"body_a":"world","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.67765,0.00356,-5e-05],"force_p95":215.46134,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":218.57927,"mean_force":187.39999,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51789,-0.0863,0.10022]},{"body_a":"push_box","body_b":"link7","contact_count":13.0,"contact_point_centroid":[0.53744,-0.03701,0.05121],"force_p95":90.33166,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":136.6922,"mean_force":17.49728,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5178,-0.08372,0.06751]},{"body_a":"world","body_b":"push_box","contact_count":3851.0,"contact_point_centroid":[0.50608,-0.03137,-2e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":84.41601,"mean_force":0.31091,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.54049,-0.06407,0.0586]},{"body_a":"world","body_b":"push_box","contact_count":2212.0,"contact_point_centroid":[0.51644,-0.02763,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50507,-0.01236,0.23981]},{"body_a":"world","body_b":"push_box","contact_count":12.0,"contact_point_centroid":[0.49279,-0.03646,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51772,-0.08568,0.09969]},{"body_a":"world","body_b":"push_box","contact_count":2060.0,"contact_point_centroid":[0.49279,-0.03646,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50823,-0.07108,0.13787]}],"total_contact_groups":10},"final_pose_error":0.01,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49279,-0.03646,0.02499],"final_tcp_position":[0.49383,-0.04267,0.16723],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51644,-0.02763,0.025]},"peak_contact_force":1031.08933,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":553.0,"n_steps_budget":600.0,"object_pos_end":[0.51644,-0.02763,0.02499],"object_pos_start":[0.51644,-0.02763,0.025],"object_to_goal_dist_end":0.12347,"object_to_goal_dist_start":0.12347,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2212.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.5123,-0.0256,0.17881],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.15389,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49279,-0.03646,0.02499],"object_pos_start":[0.51644,-0.02763,0.02499],"object_to_goal_dist_end":0.11377,"object_to_goal_dist_start":0.12347,"object_z_max":0.02714,"peak_contact_force":281.59468,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4824.0,"raw_peak_contact_force":1031.08933,"subtask_id":"reach_object","tcp_end":[0.51771,-0.08545,0.09955],"tcp_start":[0.5123,-0.0256,0.17881],"tcp_to_object_dist_end":0.09263,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.49279,-0.03646,0.02499],"object_pos_start":[0.49279,-0.03646,0.02499],"object_to_goal_dist_end":0.11377,"object_to_goal_dist_start":0.11377,"object_z_max":0.02499,"peak_contact_force":254.35917,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":15.0,"raw_peak_contact_force":254.35917,"subtask_id":"push_to_goal","tcp_end":[0.51783,-0.08625,0.10011],"tcp_start":[0.51774,-0.08594,0.09987],"tcp_to_object_dist_end":0.09353,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":515.0,"n_steps_budget":600.0,"object_pos_end":[0.49279,-0.03646,0.02499],"object_pos_start":[0.49279,-0.03646,0.02499],"object_to_goal_dist_end":0.11377,"object_to_goal_dist_start":0.11377,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2062.0,"raw_peak_contact_force":218.57927,"tcp_end":[0.49383,-0.04267,0.16723],"tcp_start":[0.51783,-0.08625,0.10011],"tcp_to_object_dist_end":0.14238,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `88c86884172a74f1f27b08fda534b767baf4d8d60d3fd4d782dec9555f4aae87`; realized-scene SHA-256: `258b33ff0697721ed1ba4810cf28d81707440dffd73b12c632f307c6591915c0`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50142,0.05406,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.00142,-0.20406,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.50142,0.05406,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.04396,"average_solve_count":91.0,"average_success_count":91.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.13302,"approach_1.approach_tolerance":0.01997,"descend_1.descend_speed":0.05075,"descend_1.descend_tolerance":0.01367,"push_1.guard_force_threshold":14.027,"push_1.push_distance":0.13737,"push_1.push_speed":0.07135,"push_1.push_tolerance":0.00717,"push_1.retry_lateral_x":0.01529,"push_1.retry_lateral_y":-0.00649,"retract_1.retract_height":0.08028,"retract_1.retract_speed":0.07608},"optimized_scores":{"best_composite_score":-0.56118,"best_fitness_score":0.09882,"best_task_score":0.07607},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"world","contact_count":32.0,"contact_point_centroid":[0.55037,0.04332,-0.00335],"force_p95":1023.06772,"geom_a":"pusher_tip","geom_b":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1083.82004,"mean_force":159.73657,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.54335,0.04497,0.00285]},{"body_a":"world","body_b":"link6","contact_count":685.0,"contact_point_centroid":[0.67159,0.02741,-0.00016],"force_p95":317.75957,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":709.32428,"mean_force":252.55438,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51576,0.11242,0.08025]},{"body_a":"world","body_b":"link7","contact_count":189.0,"contact_point_centroid":[0.59569,0.05029,-0.00029],"force_p95":373.00492,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":678.52509,"mean_force":258.23257,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53419,0.06815,0.02332]},{"body_a":"world","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.68487,0.03477,-0.00046],"force_p95":271.37482,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":272.61068,"mean_force":260.58795,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51841,0.09829,0.10826]},{"body_a":"world","body_b":"link6","contact_count":6.0,"contact_point_centroid":[0.68492,0.035,-0.00036],"force_p95":233.22278,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":234.76596,"mean_force":155.8247,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5186,0.09914,0.1083]},{"body_a":"attachment","body_b":"push_box","contact_count":31.0,"contact_point_centroid":[0.51958,0.07528,0.03817],"force_p95":51.93787,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":85.24053,"mean_force":8.79666,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52416,0.08537,0.0343]},{"body_a":"world","body_b":"push_box","contact_count":3702.0,"contact_point_centroid":[0.47933,0.04112,-3e-05],"force_p95":0.24578,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":67.52957,"mean_force":0.332,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5232,0.09795,0.07223]},{"body_a":"world","body_b":"push_box","contact_count":2444.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49833,0.02443,0.23911]},{"body_a":"world","body_b":"push_box","contact_count":12.0,"contact_point_centroid":[0.47168,0.0364,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51841,0.09829,0.10826]},{"body_a":"world","body_b":"push_box","contact_count":2740.0,"contact_point_centroid":[0.47168,0.0364,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5054,0.08382,0.14922]}],"total_contact_groups":10},"final_pose_error":0.00984,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47168,0.0364,0.02499],"final_tcp_position":[0.47609,0.04475,0.1722],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":1083.82004,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":611.0,"n_steps_budget":660.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2444.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.4984,0.05032,0.17817],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.15326,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47168,0.0364,0.02499],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.18854,"object_to_goal_dist_start":0.20406,"object_z_max":0.03031,"peak_contact_force":332.02736,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4639.0,"raw_peak_contact_force":1083.82004,"subtask_id":"reach_object","tcp_end":[0.51847,0.09801,0.10834],"tcp_start":[0.4984,0.05032,0.17817],"tcp_to_object_dist_end":0.11372,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.47168,0.0364,0.02499],"object_pos_start":[0.47168,0.0364,0.02499],"object_to_goal_dist_end":0.18854,"object_to_goal_dist_start":0.18854,"object_z_max":0.02499,"peak_contact_force":248.90106,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":15.0,"raw_peak_contact_force":272.61068,"subtask_id":"push_to_goal","tcp_end":[0.51837,0.09899,0.1081],"tcp_start":[0.51837,0.09859,0.10819],"tcp_to_object_dist_end":0.11404,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":685.0,"n_steps_budget":870.0,"object_pos_end":[0.47168,0.0364,0.02499],"object_pos_start":[0.47168,0.0364,0.02499],"object_to_goal_dist_end":0.18854,"object_to_goal_dist_start":0.18854,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2746.0,"raw_peak_contact_force":234.76596,"tcp_end":[0.47609,0.04475,0.1722],"tcp_start":[0.51837,0.09899,0.1081],"tcp_to_object_dist_end":0.14751,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a3cdbd735282928b0caf1de02aaaeed7f0a3d0a10908989412c558d20f3517fa`; realized-scene SHA-256: `8c36a5f9300ba3a57ccc09620ec8ba0a5276276ed83fb4303679e150911bfa14`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47139,-0.02418,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02861,-0.12582,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47139,-0.02418,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.30488,"average_solve_count":82.0,"average_success_count":82.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.22691,"approach_1.approach_tolerance":0.01386,"descend_1.descend_speed":0.02941,"descend_1.descend_tolerance":0.0092,"push_1.guard_force_threshold":16.50936,"push_1.push_distance":0.13294,"push_1.push_speed":0.04101,"push_1.push_tolerance":0.01331,"push_1.retry_lateral_x":0.00609,"push_1.retry_lateral_y":-0.0027,"retract_1.retract_height":0.11908,"retract_1.retract_speed":0.14283},"optimized_scores":{"best_composite_score":-0.54741,"best_fitness_score":0.11259,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"world","contact_count":22.0,"contact_point_centroid":[0.5112,-0.02707,-0.00244],"force_p95":922.3253,"geom_a":"pusher_tip","geom_b":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":942.24863,"mean_force":196.68876,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50434,-0.02792,0.00491]},{"body_a":"world","body_b":"link7","contact_count":261.0,"contact_point_centroid":[0.55793,-0.02716,-0.00023],"force_p95":328.59751,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":775.96428,"mean_force":236.49962,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49736,-0.03402,0.02745]},{"body_a":"world","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.65497,-0.00471,-3e-05],"force_p95":441.35087,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":453.25783,"mean_force":334.18821,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48628,-0.07761,0.07022]},{"body_a":"world","body_b":"link6","contact_count":638.0,"contact_point_centroid":[0.64441,-0.00592,-6e-05],"force_p95":190.45751,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":368.38344,"mean_force":186.42068,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47546,-0.05629,0.05803]},{"body_a":"world","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.65494,-0.0047,-6e-05],"force_p95":283.9382,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":284.08225,"mean_force":282.79558,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48593,-0.07715,0.06987]},{"body_a":"attachment","body_b":"push_box","contact_count":38.0,"contact_point_centroid":[0.48918,-0.02868,0.03779],"force_p95":63.81284,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":84.34189,"mean_force":7.97725,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49233,-0.03708,0.03117]},{"body_a":"world","body_b":"push_box","contact_count":3645.0,"contact_point_centroid":[0.44391,-0.01668,-5e-05],"force_p95":0.40682,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":59.77169,"mean_force":0.34044,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48455,-0.04874,0.05521]},{"body_a":"world","body_b":"push_box","contact_count":2136.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48483,-0.01088,0.2398]},{"body_a":"world","body_b":"push_box","contact_count":12.0,"contact_point_centroid":[0.43249,-0.01322,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48593,-0.07715,0.06987]},{"body_a":"world","body_b":"push_box","contact_count":2168.0,"contact_point_centroid":[0.43249,-0.01322,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.47155,-0.06302,0.12936]}],"total_contact_groups":10},"final_pose_error":0.01071,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.43249,-0.01322,0.02499],"final_tcp_position":[0.43701,-0.02151,0.16995],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":942.24863,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":534.0,"n_steps_budget":600.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2136.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.47056,-0.0224,0.17948],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.15451,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.43249,-0.01322,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.15254,"object_to_goal_dist_start":0.12903,"object_z_max":0.0292,"peak_contact_force":181.68221,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4604.0,"raw_peak_contact_force":942.24863,"subtask_id":"reach_object","tcp_end":[0.48584,-0.07697,0.06978],"tcp_start":[0.47056,-0.0224,0.17948],"tcp_to_object_dist_end":0.09443,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.43249,-0.01322,0.02499],"object_pos_start":[0.43249,-0.01322,0.02499],"object_to_goal_dist_end":0.15254,"object_to_goal_dist_start":0.15254,"object_z_max":0.02499,"peak_contact_force":281.66274,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":15.0,"raw_peak_contact_force":284.08225,"subtask_id":"push_to_goal","tcp_end":[0.48618,-0.07758,0.07008],"tcp_start":[0.48604,-0.07734,0.06996],"tcp_to_object_dist_end":0.09518,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.43249,-0.01322,0.02499],"object_pos_start":[0.43249,-0.01322,0.02499],"object_to_goal_dist_end":0.15254,"object_to_goal_dist_start":0.15254,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2170.0,"raw_peak_contact_force":453.25783,"tcp_end":[0.43701,-0.02151,0.16995],"tcp_start":[0.48618,-0.07758,0.07008],"tcp_to_object_dist_end":0.14527,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```