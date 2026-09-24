## Search State

- **Seed**: 0
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6  | 0.2439 | 0.50 | ❌ rejected |
| 13 | approach → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5  | 0.2399 | 0.81 | ❌ rejected |
| 12 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5  | 0.2391 | 0.83 | ✅ accepted |
| 11 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5  | 0.2386 | 0.82 | ❌ rejected |
| 10 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5  | 0.2556 | 0.33 | ❌ rejected |

**Proposal policy**: task_score is 0.33 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.833, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.256) — your mutation base

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

- **Composite score**: 0.256
- **task_score** (E): 0.326
- **fitness_score**: 0.616  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1714 |
| descend_1 | 1.00 | 1.00 | 0.0984 |
| push_1 | 1.00 | 1.00 | 0.1256 |
| retract_1 | 1.00 | 1.00 | 0.0881 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.494, 0.001, 0.134) | (0.496, 0.001, 0.025)→(0.496, 0.001, 0.025) | 0.152→0.152 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_1 | descend | 1.00 / step_budget | (0.494, 0.001, 0.134)→(0.516, -0.030, 0.043) | (0.496, 0.001, 0.025)→(0.502, -0.002, 0.025) | 0.152→0.150 | 1.00 / 3.667 | 224.652 | 250.364 |
| push_1 | push | 1.00 / step_budget | (0.516, -0.030, 0.043)→(0.499, -0.151, 0.023) | (0.502, -0.002, 0.025)→(0.500, -0.046, 0.025) | 0.150→0.105 | 1.00 / 4.000 | 0.245 | 172.576 |
| retract_1 | retract | 1.00 / step_budget | (0.499, -0.151, 0.023)→(0.497, -0.138, 0.110) | (0.500, -0.046, 0.025)→(0.500, -0.046, 0.025) | 0.105→0.105 | 1.00 / 4.000 | 0.245 | 0.245 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.367
- lateral_force_integral: None
- approach_alignment: 0.790
- goal_progress: 0.364
- terminal_score: 0.364
- phase_score: 0.813
- phase_breakdown.goal_push_score: 0.912
- phase_breakdown.pre_push_score: 0.581

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.633
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.383
- **Median Q (composite search score)**: 0.267
- **K-run variance**: 0.0004
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.206


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.00889,"average_solve_count":225.0,"average_success_count":225.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.07578,"descend_1.descend_speed":0.02334,"push_1.push_distance":0.11137,"push_1.push_speed":0.04479,"retract_1.retract_height":0.05808,"retract_1.retract_speed":0.09476},"optimized_scores":{"best_composite_score":0.27313,"best_fitness_score":0.63313,"best_task_score":0.36407},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":227.0,"contact_point_centroid":[0.53501,-0.04873,0.04539],"force_p95":233.23106,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":241.97786,"mean_force":217.51247,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52548,-0.05507,0.04496]},{"body_a":"world","body_b":"push_box","contact_count":1606.0,"contact_point_centroid":[0.5209,-0.03134,-0.00031],"force_p95":194.60389,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":208.16618,"mean_force":31.1903,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.517,-0.04402,0.07314]},{"body_a":"attachment","body_b":"push_box","contact_count":91.0,"contact_point_centroid":[0.53818,-0.06179,0.04511],"force_p95":152.89464,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":155.28714,"mean_force":101.3489,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53567,-0.07312,0.04422]},{"body_a":"world","body_b":"push_box","contact_count":599.0,"contact_point_centroid":[0.51783,-0.06369,-0.0004],"force_p95":114.51468,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":149.70495,"mean_force":15.82259,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51987,-0.11005,0.03319]},{"body_a":"world","body_b":"push_box","contact_count":2216.0,"contact_point_centroid":[0.51644,-0.02763,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50502,-0.0124,0.21713]},{"body_a":"world","body_b":"push_box","contact_count":1376.0,"contact_point_centroid":[0.51528,-0.07298,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24522,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49938,-0.12047,0.06448]}],"total_contact_groups":6},"final_pose_error":0.01969,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51528,-0.07298,0.02499],"final_tcp_position":[0.49742,-0.13484,0.11269],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51644,-0.02763,0.025]},"peak_contact_force":241.97786,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":554.0,"n_steps_budget":1000.0,"object_pos_end":[0.51644,-0.02763,0.02499],"object_pos_start":[0.51644,-0.02763,0.025],"object_to_goal_dist_end":0.12347,"object_to_goal_dist_start":0.12347,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2216.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_push","tcp_end":[0.51192,-0.02539,0.13363],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10876,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":458.0,"n_steps_budget":1000.0,"object_pos_end":[0.52214,-0.03026,0.02454],"object_pos_start":[0.51644,-0.02763,0.02499],"object_to_goal_dist_end":0.12177,"object_to_goal_dist_start":0.12347,"object_z_max":0.02499,"peak_contact_force":214.17707,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1833.0,"raw_peak_contact_force":241.97786,"subtask_id":"pre_push","tcp_end":[0.53645,-0.05915,0.04322],"tcp_start":[0.51192,-0.02539,0.13363],"tcp_to_object_dist_end":0.03727,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":249.0,"n_steps_budget":1000.0,"object_pos_end":[0.51528,-0.07298,0.02497],"object_pos_start":[0.52214,-0.03026,0.02454],"object_to_goal_dist_end":0.07852,"object_to_goal_dist_start":0.12177,"object_z_max":0.03578,"peak_contact_force":0.24473,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":690.0,"raw_peak_contact_force":155.28714,"subtask_id":"goal_push","tcp_end":[0.50424,-0.15029,0.02316],"tcp_start":[0.53645,-0.05915,0.04322],"tcp_to_object_dist_end":0.07812,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":344.0,"n_steps_budget":690.0,"object_pos_end":[0.51528,-0.07298,0.02499],"object_pos_start":[0.51528,-0.07298,0.02497],"object_to_goal_dist_end":0.07852,"object_to_goal_dist_start":0.07852,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1376.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49742,-0.13484,0.11269],"tcp_start":[0.50424,-0.15029,0.02316],"tcp_to_object_dist_end":0.1088,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.83582,"average_solve_count":335.0,"average_success_count":335.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.05304,"descend_1.descend_speed":0.0255,"push_1.push_distance":0.1924,"push_1.push_speed":0.03782,"retract_1.retract_height":0.1368,"retract_1.retract_speed":0.03065},"optimized_scores":{"best_composite_score":0.22654,"best_fitness_score":0.58654,"best_task_score":0.22952},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":202.0,"contact_point_centroid":[0.5199,0.0334,0.04535],"force_p95":243.64535,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":245.94467,"mean_force":222.64724,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51034,0.02713,0.04486]},{"body_a":"world","body_b":"push_box","contact_count":1485.0,"contact_point_centroid":[0.50596,0.05118,-0.0003],"force_p95":199.49842,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":211.12671,"mean_force":30.71724,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50189,0.03566,0.07464]},{"body_a":"world","body_b":"push_box","contact_count":1442.0,"contact_point_centroid":[0.50655,0.01122,-0.00017],"force_p95":25.81357,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":154.31937,"mean_force":6.56708,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5081,-0.07693,0.02998]},{"body_a":"attachment","body_b":"push_box","contact_count":95.0,"contact_point_centroid":[0.52556,0.02206,0.04527],"force_p95":150.92109,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":153.13304,"mean_force":94.79324,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52309,0.01071,0.04425]},{"body_a":"world","body_b":"push_box","contact_count":2432.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49819,0.02433,0.21668]},{"body_a":"world","body_b":"push_box","contact_count":1252.0,"contact_point_centroid":[0.50595,0.00711,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4963,-0.13698,0.06222]}],"total_contact_groups":6},"final_pose_error":0.01987,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50595,0.00711,0.02499],"final_tcp_position":[0.49679,-0.14166,0.10726],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":245.94467,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":608.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2432.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_push","tcp_end":[0.49816,0.04975,0.13316],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10831,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":427.0,"n_steps_budget":1000.0,"object_pos_end":[0.50721,0.05229,0.02453],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.20242,"object_to_goal_dist_start":0.20406,"object_z_max":0.02499,"peak_contact_force":214.4982,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1687.0,"raw_peak_contact_force":245.94467,"subtask_id":"pre_push","tcp_end":[0.52198,0.02521,0.04315],"tcp_start":[0.49816,0.04975,0.13316],"tcp_to_object_dist_end":0.03602,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":460.0,"n_steps_budget":1000.0,"object_pos_end":[0.50595,0.00711,0.02499],"object_pos_start":[0.50721,0.05229,0.02453],"object_to_goal_dist_end":0.15722,"object_to_goal_dist_start":0.20242,"object_z_max":0.03559,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1537.0,"raw_peak_contact_force":154.31937,"subtask_id":"goal_push","tcp_end":[0.49873,-0.15062,0.02168],"tcp_start":[0.52198,0.02521,0.04315],"tcp_to_object_dist_end":0.15794,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":313.0,"n_steps_budget":1000.0,"object_pos_end":[0.50595,0.00711,0.02499],"object_pos_start":[0.50595,0.00711,0.02499],"object_to_goal_dist_end":0.15722,"object_to_goal_dist_start":0.15722,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1252.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49679,-0.14166,0.10726],"tcp_start":[0.49873,-0.15062,0.02168],"tcp_to_object_dist_end":0.17025,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.04673,"average_solve_count":214.0,"average_success_count":214.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.05612,"descend_1.descend_speed":0.04023,"push_1.push_distance":0.11603,"push_1.push_speed":0.06673,"retract_1.retract_height":0.09298,"retract_1.retract_speed":0.0387},"optimized_scores":{"best_composite_score":0.26714,"best_fitness_score":0.62714,"best_task_score":0.38297},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":148.0,"contact_point_centroid":[0.48803,-0.04467,0.04537],"force_p95":260.04934,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":263.16913,"mean_force":237.41833,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47834,-0.05063,0.04493]},{"body_a":"world","body_b":"push_box","contact_count":1370.0,"contact_point_centroid":[0.47459,-0.02695,-0.00024],"force_p95":212.18468,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":229.11954,"mean_force":26.09653,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47163,-0.03867,0.07808]},{"body_a":"world","body_b":"push_box","contact_count":587.0,"contact_point_centroid":[0.4807,-0.06442,-0.00043],"force_p95":165.20487,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":208.12138,"mean_force":17.89254,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49241,-0.11424,0.03139]},{"body_a":"attachment","body_b":"push_box","contact_count":94.0,"contact_point_centroid":[0.49452,-0.06034,0.04357],"force_p95":197.69288,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":206.77401,"mean_force":109.04821,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49285,-0.0718,0.04249]},{"body_a":"world","body_b":"push_box","contact_count":2256.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48473,-0.01083,0.21758]},{"body_a":"world","body_b":"push_box","contact_count":1324.0,"contact_point_centroid":[0.47879,-0.07326,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24523,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49328,-0.13195,0.06336]}],"total_contact_groups":6},"final_pose_error":0.01978,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47879,-0.07326,0.02499],"final_tcp_position":[0.49626,-0.139,0.10899],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":263.16913,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":564.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2256.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_push","tcp_end":[0.47056,-0.02219,0.13452],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10956,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":379.0,"n_steps_budget":1000.0,"object_pos_end":[0.47677,-0.02697,0.02446],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.1252,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":245.27997,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1518.0,"raw_peak_contact_force":263.16913,"subtask_id":"pre_push","tcp_end":[0.48883,-0.05468,0.04251],"tcp_start":[0.47056,-0.02219,0.13452],"tcp_to_object_dist_end":0.03519,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":247.0,"n_steps_budget":1000.0,"object_pos_end":[0.47879,-0.07326,0.02498],"object_pos_start":[0.47677,-0.02697,0.02446],"object_to_goal_dist_end":0.07962,"object_to_goal_dist_start":0.1252,"object_z_max":0.03525,"peak_contact_force":0.24496,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":681.0,"raw_peak_contact_force":208.12138,"subtask_id":"goal_push","tcp_end":[0.49342,-0.1519,0.02301],"tcp_start":[0.48883,-0.05468,0.04251],"tcp_to_object_dist_end":0.08002,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":331.0,"n_steps_budget":1000.0,"object_pos_end":[0.47879,-0.07326,0.02499],"object_pos_start":[0.47879,-0.07326,0.02498],"object_to_goal_dist_end":0.07962,"object_to_goal_dist_start":0.07962,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1324.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49626,-0.139,0.10899],"tcp_start":[0.49342,-0.1519,0.02301],"tcp_to_object_dist_end":0.10809,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```