## Search State

- **Seed**: 0
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.2392 | 0.81 | ❌ rejected |
| 1 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.2365 | 0.82 | ✅ accepted |
| 0 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.2276 | 0.80 | ✅ accepted |

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

## Current Skill (Q=0.239) — your mutation base

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

- **Composite score**: 0.239
- **task_score** (E): 0.806
- **fitness_score**: 0.609  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.370

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| insert_1 | 0.00 | 1.00 | 0.1849 |
| approach_1 | 1.00 | 1.00 | 0.1925 |
| push_1 | 1.00 | 1.00 | 0.1675 |
| retract_1 | 0.00 | 1.00 | 0.1149 |
| lift_1 | 0.00 | 1.00 | 0.1467 |
| insert_2 | 0.00 | 1.00 | 0.1668 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| insert_1 | insert | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.497, -0.086, 0.137) | (0.496, 0.001, 0.025)→(0.496, 0.001, 0.025) | 0.152→0.152 | 1.00 / 4.000 | 0.245 | 0.245 |
| approach_1 | approach | 1.00 / step_budget | (0.497, -0.086, 0.137)→(0.494, 0.071, 0.030) | (0.496, 0.001, 0.025)→(0.497, 0.010, 0.028) | 0.152→0.161 | 1.00 / 4.000 | 13.603 | 60.704 |
| push_1 | push | 1.00 / step_budget | (0.494, 0.071, 0.030)→(0.496, -0.096, 0.023) | (0.497, 0.010, 0.028)→(0.494, -0.134, 0.029) | 0.161→0.033 | 1.00 / 3.333 | 28.993 | 55.856 |
| retract_1 | retract | 0.00 / step_budget | (0.496, -0.096, 0.023)→(0.494, -0.007, 0.095) | (0.494, -0.134, 0.029)→(0.494, -0.128, 0.025) | 0.033→0.035 | 1.00 / 4.000 | 0.245 | 23.854 |
| lift_1 | lift | 0.00 / step_budget | (0.494, -0.007, 0.095)→(0.426, -0.071, 0.207) | (0.494, -0.128, 0.025)→(0.494, -0.128, 0.025) | 0.035→0.035 | 1.00 / 4.000 | 0.245 | 0.245 |
| insert_2 | insert | 0.00 / step_budget | (0.426, -0.071, 0.207)→(0.479, -0.131, 0.061) | (0.494, -0.128, 0.025)→(0.494, -0.128, 0.025) | 0.035→0.035 | 1.00 / 4.000 | 0.245 | 0.245 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.744
- goal_progress: 0.915
- terminal_score: 0.915
- phase_score: 0.637
- phase_breakdown.approach_score: 0.820
- phase_breakdown.push_score: 0.946
- phase_breakdown.contact_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.748
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.923
- **Median Q (composite search score)**: 0.335
- **K-run variance**: 0.0278
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Parameters at upper bound**: push_1.push_speed
- **Final σ (mean)**: 0.473


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.53409,"average_solve_count":264.0,"average_success_count":264.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.speed":0.01792,"push_1.push_distance":0.13042,"push_1.push_speed":0.08268,"retract_1.retract_height":0.06219,"retract_1.speed":0.03685},"optimized_scores":{"best_composite_score":0.37825,"best_fitness_score":0.74825,"best_task_score":0.91523},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1821.0,"contact_point_centroid":[0.51479,-0.07819,-7e-05],"force_p95":38.64456,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":58.81946,"mean_force":7.50498,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50381,-0.02562,0.02167]},{"body_a":"attachment","body_b":"push_box","contact_count":692.0,"contact_point_centroid":[0.51423,-0.07778,0.04555],"force_p95":40.39411,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":53.1703,"mean_force":12.65429,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50148,-0.06611,0.02119]},{"body_a":"push_box","body_b":"link7","contact_count":452.0,"contact_point_centroid":[0.53158,-0.08864,0.05199],"force_p95":31.42337,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.99166,"mean_force":14.99481,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50161,-0.06933,0.02143]},{"body_a":"push_box","body_b":"link7","contact_count":13.0,"contact_point_centroid":[0.52649,-0.14812,0.05453],"force_p95":33.85828,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.79719,"mean_force":16.92925,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49978,-0.12516,0.02228]},{"body_a":"attachment","body_b":"push_box","contact_count":46.0,"contact_point_centroid":[0.51764,-0.13299,0.05411],"force_p95":23.30124,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.42317,"mean_force":3.95828,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49851,-0.12227,0.02354]},{"body_a":"world","body_b":"push_box","contact_count":3844.0,"contact_point_centroid":[0.50399,-0.16039,-1e-05],"force_p95":0.24584,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.28333,"mean_force":0.27904,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4963,-0.07756,0.05931]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.51644,-0.02763,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49729,-0.0436,0.21555]},{"body_a":"world","body_b":"push_box","contact_count":2704.0,"contact_point_centroid":[0.51644,-0.02763,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50252,-0.02032,0.07916]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.50373,-0.15978,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4606,-0.05718,0.14634]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.50373,-0.15978,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.45365,-0.10952,0.1288]}],"total_contact_groups":10},"final_pose_error":0.03778,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50373,-0.15978,0.02499],"final_tcp_position":[0.48208,-0.13619,0.05525],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51644,-0.02763,0.025]},"peak_contact_force":58.81946,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51644,-0.02763,0.02499],"object_pos_start":[0.51644,-0.02763,0.025],"object_to_goal_dist_end":0.12347,"object_to_goal_dist_start":0.12347,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.4966,-0.08596,0.13695],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12779,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":676.0,"n_steps_budget":1000.0,"object_pos_end":[0.51644,-0.02763,0.02499],"object_pos_start":[0.51644,-0.02763,0.02499],"object_to_goal_dist_end":0.12347,"object_to_goal_dist_start":0.12347,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2704.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.51104,0.04412,0.02621],"tcp_start":[0.4966,-0.08596,0.13695],"tcp_to_object_dist_end":0.07196,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50621,-0.16275,0.02839],"object_pos_start":[0.51644,-0.02763,0.02499],"object_to_goal_dist_end":0.01458,"object_to_goal_dist_start":0.12347,"object_z_max":0.03005,"peak_contact_force":43.77402,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2965.0,"raw_peak_contact_force":58.81946,"tcp_end":[0.50018,-0.12524,0.02224],"tcp_start":[0.51104,0.04412,0.02621],"tcp_to_object_dist_end":0.03849,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50373,-0.15978,0.02499],"object_pos_start":[0.50621,-0.16275,0.02839],"object_to_goal_dist_end":0.01047,"object_to_goal_dist_start":0.01458,"object_z_max":0.02849,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3903.0,"raw_peak_contact_force":35.79719,"tcp_end":[0.49641,-0.0307,0.09275],"tcp_start":[0.50018,-0.12524,0.02224],"tcp_to_object_dist_end":0.14597,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50373,-0.15978,0.02499],"object_pos_start":[0.50373,-0.15978,0.02499],"object_to_goal_dist_end":0.01047,"object_to_goal_dist_start":0.01047,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.42821,-0.08376,0.20408],"tcp_start":[0.49641,-0.0307,0.09275],"tcp_to_object_dist_end":0.2087,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50373,-0.15978,0.02499],"object_pos_start":[0.50373,-0.15978,0.02499],"object_to_goal_dist_end":0.01047,"object_to_goal_dist_start":0.01047,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.48208,-0.13619,0.05525],"tcp_start":[0.42821,-0.08376,0.20408],"tcp_to_object_dist_end":0.04406,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.52158,"average_solve_count":278.0,"average_success_count":278.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.speed":0.0445,"push_1.push_distance":0.16142,"push_1.push_speed":0.1,"retract_1.retract_height":0.13339,"retract_1.speed":0.03815},"optimized_scores":{"best_composite_score":0.00468,"best_fitness_score":0.37468,"best_task_score":0.57861},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":286.0,"contact_point_centroid":[0.51033,0.08541,0.04646],"force_p95":154.66051,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":181.6215,"mean_force":112.54583,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50235,0.09183,0.04903]},{"body_a":"world","body_b":"push_box","contact_count":3422.0,"contact_point_centroid":[0.50174,0.05825,-9e-05],"force_p95":81.58625,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":164.76933,"mean_force":9.73416,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49612,0.00715,0.08615]},{"body_a":"attachment","body_b":"push_box","contact_count":994.0,"contact_point_centroid":[0.50387,0.03333,0.03067],"force_p95":76.47719,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":81.60241,"mean_force":56.1479,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50191,0.04458,0.03124]},{"body_a":"world","body_b":"push_box","contact_count":1926.0,"contact_point_centroid":[0.49628,-0.00246,-0.00018],"force_p95":61.50211,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":75.61604,"mean_force":42.0134,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50194,0.04693,0.0314]},{"body_a":"push_box","body_b":"link7","contact_count":1000.0,"contact_point_centroid":[0.52172,0.01009,0.0679],"force_p95":33.96969,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":53.8641,"mean_force":31.66359,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5019,0.04505,0.03126]},{"body_a":"push_box","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.52838,0.09012,0.06853],"force_p95":39.95326,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.31824,"mean_force":36.49581,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50206,0.12188,0.0353]},{"body_a":"push_box","body_b":"link7","contact_count":19.0,"contact_point_centroid":[0.50842,-0.07617,0.06682],"force_p95":24.81545,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.40017,"mean_force":7.55981,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49906,-0.04018,0.02507]},{"body_a":"world","body_b":"push_box","contact_count":3723.0,"contact_point_centroid":[0.4839,-0.06683,-1e-05],"force_p95":0.36423,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.44543,"mean_force":0.29989,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49588,-0.00053,0.06522]},{"body_a":"attachment","body_b":"push_box","contact_count":56.0,"contact_point_centroid":[0.49526,-0.04665,0.03026],"force_p95":2.52832,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.60482,"mean_force":0.89199,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49704,-0.03493,0.0294]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49729,-0.0436,0.21555]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.4844,-0.06544,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46154,-0.00259,0.1491]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.4844,-0.06544,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.45308,-0.0822,0.13337]}],"total_contact_groups":12},"final_pose_error":0.05304,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.4844,-0.06544,0.02499],"final_tcp_position":[0.47877,-0.12243,0.06503],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":181.6215,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.4966,-0.08596,0.13695],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.17934,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50341,0.08175,0.03419],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.23196,"object_to_goal_dist_start":0.20406,"object_z_max":0.03486,"peak_contact_force":40.31824,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3711.0,"raw_peak_contact_force":181.6215,"tcp_end":[0.50193,0.12221,0.03486],"tcp_start":[0.4966,-0.08596,0.13695],"tcp_to_object_dist_end":0.04049,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48215,-0.07941,0.03336],"object_pos_start":[0.50341,0.08175,0.03419],"object_to_goal_dist_end":0.07329,"object_to_goal_dist_start":0.23196,"object_z_max":0.0342,"peak_contact_force":41.56869,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3920.0,"raw_peak_contact_force":81.60241,"tcp_end":[0.49963,-0.04025,0.02484],"tcp_start":[0.50193,0.12221,0.03486],"tcp_to_object_dist_end":0.04373,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4844,-0.06544,0.02499],"object_pos_start":[0.48215,-0.07941,0.03336],"object_to_goal_dist_end":0.08599,"object_to_goal_dist_start":0.07329,"object_z_max":0.03363,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3798.0,"raw_peak_contact_force":25.40017,"tcp_end":[0.49615,0.0382,0.09877],"tcp_start":[0.49963,-0.04025,0.02484],"tcp_to_object_dist_end":0.12776,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4844,-0.06544,0.02499],"object_pos_start":[0.4844,-0.06544,0.02499],"object_to_goal_dist_end":0.08599,"object_to_goal_dist_start":0.08599,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.43033,-0.04301,0.20351],"tcp_start":[0.49615,0.0382,0.09877],"tcp_to_object_dist_end":0.18787,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4844,-0.06544,0.02499],"object_pos_start":[0.4844,-0.06544,0.02499],"object_to_goal_dist_end":0.08599,"object_to_goal_dist_start":0.08599,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.47877,-0.12243,0.06503],"tcp_start":[0.43033,-0.04301,0.20351],"tcp_to_object_dist_end":0.06988,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.63386,"average_solve_count":254.0,"average_success_count":254.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.speed":0.06563,"push_1.push_distance":0.14313,"push_1.push_speed":0.09219,"retract_1.retract_height":0.12335,"retract_1.speed":0.04586},"optimized_scores":{"best_composite_score":0.33471,"best_fitness_score":0.70471,"best_task_score":0.92321},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":746.0,"contact_point_centroid":[0.48548,-0.06815,0.03258],"force_p95":17.01246,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.14718,"mean_force":4.07106,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47992,-0.05616,0.02171]},{"body_a":"world","body_b":"push_box","contact_count":1988.0,"contact_point_centroid":[0.4787,-0.0733,-3e-05],"force_p95":7.68392,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.31748,"mean_force":1.82508,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47565,-0.02469,0.02252]},{"body_a":"push_box","body_b":"link7","contact_count":13.0,"contact_point_centroid":[0.51987,-0.14451,0.05014],"force_p95":7.58609,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.36412,"mean_force":2.3907,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48858,-0.12142,0.02071]},{"body_a":"world","body_b":"push_box","contact_count":3962.0,"contact_point_centroid":[0.49477,-0.15855,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.0166,"mean_force":0.2558,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48748,-0.07543,0.05749]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.50347,-0.13407,0.05001],"force_p95":1.11655,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.17532,"mean_force":0.58766,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48947,-0.1219,0.0206]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49729,-0.0436,0.21555]},{"body_a":"world","body_b":"push_box","contact_count":2520.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48142,-0.0196,0.08025]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.49489,-0.15849,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45279,-0.05667,0.15083]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.49489,-0.15849,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.44715,-0.10972,0.13767]}],"total_contact_groups":9},"final_pose_error":0.04773,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49489,-0.15849,0.02499],"final_tcp_position":[0.47758,-0.13429,0.0641],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":27.14718,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.4966,-0.08596,0.13695],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13033,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":630.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2520.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.46892,0.04665,0.02746],"tcp_start":[0.4966,-0.08596,0.13695],"tcp_to_object_dist_end":0.07092,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4951,-0.15887,0.02504],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.01013,"object_to_goal_dist_start":0.12903,"object_z_max":0.02538,"peak_contact_force":1.63729,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2734.0,"raw_peak_contact_force":27.14718,"tcp_end":[0.48948,-0.12185,0.02061],"tcp_start":[0.46892,0.04665,0.02746],"tcp_to_object_dist_end":0.03771,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49489,-0.15849,0.02499],"object_pos_start":[0.4951,-0.15887,0.02504],"object_to_goal_dist_end":0.00991,"object_to_goal_dist_start":0.01013,"object_z_max":0.02517,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3977.0,"raw_peak_contact_force":10.36412,"tcp_end":[0.48945,-0.02722,0.09249],"tcp_start":[0.48948,-0.12185,0.02061],"tcp_to_object_dist_end":0.14771,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49489,-0.15849,0.02499],"object_pos_start":[0.49489,-0.15849,0.02499],"object_to_goal_dist_end":0.00991,"object_to_goal_dist_start":0.00991,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.41969,-0.08604,0.21286],"tcp_start":[0.48945,-0.02722,0.09249],"tcp_to_object_dist_end":0.21494,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49489,-0.15849,0.02499],"object_pos_start":[0.49489,-0.15849,0.02499],"object_to_goal_dist_end":0.00991,"object_to_goal_dist_start":0.00991,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.47758,-0.13429,0.0641],"tcp_start":[0.41969,-0.08604,0.21286],"tcp_to_object_dist_end":0.04915,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```