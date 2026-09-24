## Search State

- **Seed**: 0
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.2402 | 0.81 | ❌ rejected |
| 8 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.2405 | 0.81 | ❌ rejected |
| 7 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.2427 | 0.82 | ✅ accepted |
| 6 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.2398 | 0.81 | ❌ rejected |
| 5 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.2375 | 0.81 | ❌ rejected |

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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.817, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.240) — your mutation base

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

- **Composite score**: 0.240
- **task_score** (E): 0.811
- **fitness_score**: 0.610  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.370

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| insert_1 | 0.00 | 1.00 | 0.1849 |
| approach_1 | 1.00 | 1.00 | 0.1925 |
| push_1 | 0.67 | 1.00 | 0.1668 |
| retract_1 | 0.00 | 1.00 | 0.1225 |
| lift_1 | 0.00 | 1.00 | 0.1507 |
| insert_2 | 0.00 | 1.00 | 0.1653 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| insert_1 | insert | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.497, -0.086, 0.137) | (0.496, 0.001, 0.025)→(0.496, 0.001, 0.025) | 0.152→0.152 | 1.00 / 4.000 | 0.245 | 0.245 |
| approach_1 | approach | 1.00 / step_budget | (0.497, -0.086, 0.137)→(0.494, 0.071, 0.030) | (0.496, 0.001, 0.025)→(0.497, 0.010, 0.028) | 0.152→0.161 | 1.00 / 4.000 | 13.603 | 60.704 |
| push_1 | push | 0.67 / step_budget | (0.494, 0.071, 0.030)→(0.497, -0.095, 0.023) | (0.497, 0.010, 0.028)→(0.494, -0.133, 0.029) | 0.161→0.031 | 1.00 / 3.000 | 24.188 | 55.404 |
| retract_1 | retract | 0.00 / step_budget | (0.497, -0.095, 0.023)→(0.494, 0.001, 0.099) | (0.494, -0.133, 0.029)→(0.494, -0.128, 0.025) | 0.031→0.034 | 1.00 / 4.000 | 0.245 | 18.248 |
| lift_1 | lift | 0.00 / step_budget | (0.494, 0.001, 0.099)→(0.425, -0.068, 0.212) | (0.494, -0.128, 0.025)→(0.494, -0.128, 0.025) | 0.034→0.034 | 1.00 / 4.000 | 0.245 | 0.245 |
| insert_2 | insert | 0.00 / step_budget | (0.425, -0.068, 0.212)→(0.477, -0.128, 0.068) | (0.494, -0.128, 0.025)→(0.494, -0.128, 0.025) | 0.034→0.034 | 1.00 / 4.000 | 0.245 | 0.245 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.753
- goal_progress: 0.915
- terminal_score: 0.915
- phase_score: 0.632
- phase_breakdown.contact_score: 0.000
- phase_breakdown.approach_score: 0.820
- phase_breakdown.push_score: 0.936

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.745
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.927
- **Median Q (composite search score)**: 0.333
- **K-run variance**: 0.0263
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Parameters at upper bound**: push_1.push_speed
- **Final σ (mean)**: 0.320


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.7247,"average_solve_count":247.0,"average_success_count":247.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.speed":0.076,"push_1.push_distance":0.1393,"push_1.push_speed":0.09806,"retract_1.retract_height":0.14607,"retract_1.speed":0.03722},"optimized_scores":{"best_composite_score":0.37503,"best_fitness_score":0.74503,"best_task_score":0.91478},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":775.0,"contact_point_centroid":[0.51914,-0.07221,0.0475],"force_p95":49.76714,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":57.17687,"mean_force":27.46489,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5034,-0.0615,0.02251]},{"body_a":"world","body_b":"push_box","contact_count":2001.0,"contact_point_centroid":[0.51853,-0.08292,-7e-05],"force_p95":38.53479,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":53.72775,"mean_force":15.08231,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50472,-0.02879,0.02247]},{"body_a":"push_box","body_b":"link7","contact_count":775.0,"contact_point_centroid":[0.53033,-0.07833,0.05466],"force_p95":42.34758,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.77801,"mean_force":24.64162,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50349,-0.06003,0.02252]},{"body_a":"push_box","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.52529,-0.14855,0.05451],"force_p95":22.04027,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.24831,"mean_force":18.17958,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5,-0.12412,0.0218]},{"body_a":"attachment","body_b":"push_box","contact_count":36.0,"contact_point_centroid":[0.51731,-0.13266,0.05362],"force_p95":16.91412,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.67785,"mean_force":2.77681,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49862,-0.12175,0.02272]},{"body_a":"world","body_b":"push_box","contact_count":3865.0,"contact_point_centroid":[0.50341,-0.16041,-2e-05],"force_p95":0.24537,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.5089,"mean_force":0.26534,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49628,-0.07682,0.05871]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.51644,-0.02763,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49729,-0.0436,0.21555]},{"body_a":"world","body_b":"push_box","contact_count":2704.0,"contact_point_centroid":[0.51644,-0.02763,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50252,-0.02032,0.07916]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.50342,-0.15995,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4566,-0.05991,0.1533]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.50342,-0.15995,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.4467,-0.11171,0.14285]}],"total_contact_groups":10},"final_pose_error":0.05229,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50342,-0.15995,0.02499],"final_tcp_position":[0.47624,-0.13418,0.06881],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51644,-0.02763,0.025]},"peak_contact_force":57.17687,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51644,-0.02763,0.02499],"object_pos_start":[0.51644,-0.02763,0.025],"object_to_goal_dist_end":0.12347,"object_to_goal_dist_start":0.12347,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.4966,-0.08596,0.13695],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12779,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":676.0,"n_steps_budget":1000.0,"object_pos_end":[0.51644,-0.02763,0.02499],"object_pos_start":[0.51644,-0.02763,0.02499],"object_to_goal_dist_end":0.12347,"object_to_goal_dist_start":0.12347,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2704.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.51104,0.04412,0.02621],"tcp_start":[0.4966,-0.08596,0.13695],"tcp_to_object_dist_end":0.07196,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50411,-0.16257,0.02866],"object_pos_start":[0.51644,-0.02763,0.02499],"object_to_goal_dist_end":0.01372,"object_to_goal_dist_start":0.12347,"object_z_max":0.02924,"peak_contact_force":44.9748,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3551.0,"raw_peak_contact_force":57.17687,"tcp_end":[0.50017,-0.12394,0.02186],"tcp_start":[0.51104,0.04412,0.02621],"tcp_to_object_dist_end":0.03942,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50342,-0.15995,0.02499],"object_pos_start":[0.50411,-0.16257,0.02866],"object_to_goal_dist_end":0.01052,"object_to_goal_dist_start":0.01372,"object_z_max":0.02866,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3907.0,"raw_peak_contact_force":22.24831,"tcp_end":[0.4964,-0.02992,0.09241],"tcp_start":[0.50017,-0.12394,0.02186],"tcp_to_object_dist_end":0.14664,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50342,-0.15995,0.02499],"object_pos_start":[0.50342,-0.15995,0.02499],"object_to_goal_dist_end":0.01052,"object_to_goal_dist_start":0.01052,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.42007,-0.09009,0.21853],"tcp_start":[0.4964,-0.02992,0.09241],"tcp_to_object_dist_end":0.22201,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50342,-0.15995,0.02499],"object_pos_start":[0.50342,-0.15995,0.02499],"object_to_goal_dist_end":0.01052,"object_to_goal_dist_start":0.01052,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.47624,-0.13418,0.06881],"tcp_start":[0.42007,-0.09009,0.21853],"tcp_to_object_dist_end":0.05765,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.71094,"average_solve_count":256.0,"average_success_count":256.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.speed":0.03804,"push_1.push_distance":0.18877,"push_1.push_speed":0.1,"retract_1.retract_height":0.15521,"retract_1.speed":0.07718},"optimized_scores":{"best_composite_score":0.0123,"best_fitness_score":0.3823,"best_task_score":0.59172},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":286.0,"contact_point_centroid":[0.51033,0.08541,0.04646],"force_p95":154.66051,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":181.6215,"mean_force":112.54583,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50235,0.09183,0.04903]},{"body_a":"world","body_b":"push_box","contact_count":3422.0,"contact_point_centroid":[0.50174,0.05825,-9e-05],"force_p95":81.58625,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":164.76933,"mean_force":9.73416,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49612,0.00715,0.08615]},{"body_a":"attachment","body_b":"push_box","contact_count":994.0,"contact_point_centroid":[0.50374,0.0322,0.03083],"force_p95":75.12461,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":80.36649,"mean_force":54.76719,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50173,0.04346,0.03143]},{"body_a":"world","body_b":"push_box","contact_count":1912.0,"contact_point_centroid":[0.49655,-0.00309,-0.00016],"force_p95":59.12106,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":73.37764,"mean_force":40.50266,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50177,0.04629,0.0316]},{"body_a":"push_box","body_b":"link7","contact_count":1000.0,"contact_point_centroid":[0.52171,0.00885,0.068],"force_p95":31.6795,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":53.8641,"mean_force":29.15313,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50172,0.04393,0.03145]},{"body_a":"push_box","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.52838,0.09012,0.06853],"force_p95":39.95326,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.31824,"mean_force":36.49581,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50206,0.12188,0.0353]},{"body_a":"world","body_b":"push_box","contact_count":3781.0,"contact_point_centroid":[0.4846,-0.0691,-1e-05],"force_p95":0.28755,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.45613,"mean_force":0.28849,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4958,0.00717,0.07327]},{"body_a":"push_box","body_b":"link7","contact_count":11.0,"contact_point_centroid":[0.50899,-0.07891,0.06699],"force_p95":29.27057,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.2164,"mean_force":10.07657,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49909,-0.04249,0.02553]},{"body_a":"attachment","body_b":"push_box","contact_count":45.0,"contact_point_centroid":[0.49497,-0.0481,0.0315],"force_p95":3.14328,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.28455,"mean_force":0.79699,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49687,-0.03652,0.03056]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49729,-0.0436,0.21555]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.48495,-0.06806,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46117,0.01149,0.15989]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.48495,-0.06806,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.4509,-0.07367,0.14345]}],"total_contact_groups":12},"final_pose_error":0.06707,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48495,-0.06806,0.02499],"final_tcp_position":[0.47527,-0.1146,0.07631],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":181.6215,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.4966,-0.08596,0.13695],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.17934,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50341,0.08175,0.03419],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.23196,"object_to_goal_dist_start":0.20406,"object_z_max":0.03486,"peak_contact_force":40.31824,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3711.0,"raw_peak_contact_force":181.6215,"tcp_end":[0.50193,0.12221,0.03486],"tcp_start":[0.4966,-0.08596,0.13695],"tcp_to_object_dist_end":0.04049,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48247,-0.0819,0.03348],"object_pos_start":[0.50341,0.08175,0.03419],"object_to_goal_dist_end":0.07083,"object_to_goal_dist_start":0.23196,"object_z_max":0.0343,"peak_contact_force":26.34825,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3906.0,"raw_peak_contact_force":80.36649,"tcp_end":[0.49938,-0.04236,0.02536],"tcp_start":[0.50193,0.12221,0.03486],"tcp_to_object_dist_end":0.04375,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48495,-0.06806,0.02499],"object_pos_start":[0.48247,-0.0819,0.03348],"object_to_goal_dist_end":0.08331,"object_to_goal_dist_start":0.07083,"object_z_max":0.03364,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3837.0,"raw_peak_contact_force":31.45613,"tcp_end":[0.49618,0.05712,0.11155],"tcp_start":[0.49938,-0.04236,0.02536],"tcp_to_object_dist_end":0.15261,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48495,-0.06806,0.02499],"object_pos_start":[0.48495,-0.06806,0.02499],"object_to_goal_dist_end":0.08331,"object_to_goal_dist_start":0.08331,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.4294,-0.03373,0.21241],"tcp_start":[0.49618,0.05712,0.11155],"tcp_to_object_dist_end":0.19847,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48495,-0.06806,0.02499],"object_pos_start":[0.48495,-0.06806,0.02499],"object_to_goal_dist_end":0.08331,"object_to_goal_dist_start":0.08331,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.47527,-0.1146,0.07631],"tcp_start":[0.4294,-0.03373,0.21241],"tcp_to_object_dist_end":0.06996,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.5283,"average_solve_count":265.0,"average_success_count":265.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.speed":0.04935,"push_1.push_distance":0.13534,"push_1.push_speed":0.08534,"retract_1.retract_height":0.11948,"retract_1.speed":0.01883},"optimized_scores":{"best_composite_score":0.33313,"best_fitness_score":0.70313,"best_task_score":0.92728},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":741.0,"contact_point_centroid":[0.48502,-0.06633,0.03111],"force_p95":17.0394,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.66891,"mean_force":4.26431,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48022,-0.05432,0.02169]},{"body_a":"world","body_b":"push_box","contact_count":2040.0,"contact_point_centroid":[0.47825,-0.07229,-3e-05],"force_p95":7.51889,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.41976,"mean_force":1.83967,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47597,-0.02422,0.02249]},{"body_a":"world","body_b":"push_box","contact_count":3984.0,"contact_point_centroid":[0.49413,-0.15732,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.03978,"mean_force":0.24645,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48788,-0.07321,0.05723]},{"body_a":"attachment","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.50049,-0.13122,0.04272],"force_p95":0.30572,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3336,"mean_force":0.15749,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4899,-0.11912,0.02053]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49729,-0.0436,0.21555]},{"body_a":"world","body_b":"push_box","contact_count":2520.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48142,-0.0196,0.08025]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.49414,-0.15732,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45525,-0.05302,0.1466]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.49414,-0.15732,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.45047,-0.10724,0.13099]}],"total_contact_groups":8},"final_pose_error":0.04238,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49414,-0.15732,0.02499],"final_tcp_position":[0.47992,-0.13437,0.05889],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":28.66891,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.4966,-0.08596,0.13695],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13033,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":630.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2520.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.46892,0.04665,0.02746],"tcp_start":[0.4966,-0.08596,0.13695],"tcp_to_object_dist_end":0.07092,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49392,-0.15585,0.02514],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.00844,"object_to_goal_dist_start":0.12903,"object_z_max":0.02529,"peak_contact_force":1.24201,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2781.0,"raw_peak_contact_force":28.66891,"tcp_end":[0.48996,-0.11899,0.02057],"tcp_start":[0.46892,0.04665,0.02746],"tcp_to_object_dist_end":0.03735,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49414,-0.15732,0.02499],"object_pos_start":[0.49392,-0.15585,0.02514],"object_to_goal_dist_end":0.00938,"object_to_goal_dist_start":0.00844,"object_z_max":0.02514,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3988.0,"raw_peak_contact_force":1.03978,"tcp_end":[0.48978,-0.02505,0.09245],"tcp_start":[0.48996,-0.11899,0.02057],"tcp_to_object_dist_end":0.14854,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49414,-0.15732,0.02499],"object_pos_start":[0.49414,-0.15732,0.02499],"object_to_goal_dist_end":0.00938,"object_to_goal_dist_start":0.00938,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.42408,-0.08105,0.2048],"tcp_start":[0.48978,-0.02505,0.09245],"tcp_to_object_dist_end":0.2075,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49414,-0.15732,0.02499],"object_pos_start":[0.49414,-0.15732,0.02499],"object_to_goal_dist_end":0.00938,"object_to_goal_dist_start":0.00938,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.47992,-0.13437,0.05889],"tcp_start":[0.42408,-0.08105,0.2048],"tcp_to_object_dist_end":0.04334,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```