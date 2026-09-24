## Search State

- **Seed**: 3
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4557 | 0.63 | ❌ rejected |
| 7 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 5 | 0.2069 | 0.41 | ❌ rejected |
| 6 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 4 | -0.1333 | 0.00 | ❌ rejected |
| 5 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4639 | 0.71 | ❌ rejected |
| 4 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4751 | 0.73 | ✅ accepted |

**Proposal policy**: task_score is 0.63 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.456) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: contact_detected
  parameters:
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance

```

## Design Metrics

- **Composite score**: 0.456
- **task_score** (E): 0.634
- **fitness_score**: 0.666  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2843 |
| contact_1 | 1.00 | 1.00 | 0.0493 |
| push_1 | 1.00 | 1.00 | 0.1265 |
| retract_1 | 0.00 | 1.00 | 0.1668 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.509, 0.078, 0.032) | (0.513, 0.002, 0.025)→(0.513, 0.002, 0.025) | 0.160→0.160 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.509, 0.078, 0.032)→(0.509, 0.030, 0.020) | (0.513, 0.002, 0.025)→(0.515, -0.007, 0.025) | 0.160→0.152 | 1.00 / 3.333 | 5.744 | 10.470 |
| push_1 | push | 1.00 / step_budget | (0.509, 0.030, 0.020)→(0.504, -0.090, 0.026) | (0.515, -0.007, 0.025)→(0.509, -0.113, 0.029) | 0.152→0.059 | 1.00 / 4.000 | 77.842 | 108.561 |
| retract_1 | retract | 0.00 / step_budget | (0.504, -0.090, 0.026)→(0.497, 0.059, 0.099) | (0.509, -0.113, 0.029)→(0.503, -0.110, 0.025) | 0.059→0.058 | 1.00 / 4.000 | 0.245 | 62.555 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.825
- lateral_force_integral: None
- approach_alignment: 0.435
- goal_progress: 0.611
- terminal_score: 0.611
- phase_score: 0.850
- phase_breakdown.contact_score: 0.880
- phase_breakdown.approach_score: 0.820
- phase_breakdown.push_score: 0.844

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.754
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.668
- **Median Q (composite search score)**: 0.456
- **K-run variance**: 0.0052
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.425


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.26667,"average_solve_count":210.0,"average_success_count":210.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.01003,"contact_1.speed":0.04689,"push_1.push_depth":0.0923},"optimized_scores":{"best_composite_score":0.54412,"best_fitness_score":0.75412,"best_task_score":0.61057},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1368.0,"contact_point_centroid":[0.45653,-0.11051,-8e-05],"force_p95":42.52557,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":58.55007,"mean_force":7.12265,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47282,-0.07413,0.01948]},{"body_a":"attachment","body_b":"push_box","contact_count":592.0,"contact_point_centroid":[0.47193,-0.06754,0.03245],"force_p95":31.39992,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.56263,"mean_force":11.46199,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46605,-0.05621,0.01962]},{"body_a":"push_box","body_b":"link7","contact_count":219.0,"contact_point_centroid":[0.48037,-0.04406,0.05051],"force_p95":28.25865,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.7698,"mean_force":19.82288,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.45257,-0.01929,0.02029]},{"body_a":"attachment","body_b":"push_box","contact_count":110.0,"contact_point_centroid":[0.45545,-0.0106,0.03671],"force_p95":9.2852,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.15002,"mean_force":3.98879,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4461,0.00128,0.02241]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.48629,-0.13415,0.02312],"force_p95":11.98853,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.98853,"mean_force":11.98853,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49325,-0.12496,0.01985]},{"body_a":"world","body_b":"push_box","contact_count":2283.0,"contact_point_centroid":[0.45022,-0.03308,-1e-05],"force_p95":1.86379,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.4616,"mean_force":0.45016,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44578,0.02264,0.02656]},{"body_a":"world","body_b":"push_box","contact_count":3982.0,"contact_point_centroid":[0.45157,-0.13756,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.40497,"mean_force":0.24897,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49136,-0.04695,0.05205]},{"body_a":"push_box","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.47659,-0.02026,0.04998],"force_p95":4.79305,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.87594,"mean_force":3.30425,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44623,-0.00266,0.02171]},{"body_a":"world","body_b":"push_box","contact_count":3712.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47374,0.02259,0.16679]}],"total_contact_groups":9},"final_pose_error":0.13774,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.45156,-0.13756,0.02499],"final_tcp_position":[0.49329,0.02754,0.08732],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":58.55007,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":928.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3712.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.4489,0.04564,0.03445],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07781,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":630.0,"n_steps_budget":720.0,"object_pos_end":[0.45169,-0.03969,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12042,"object_to_goal_dist_start":0.12843,"object_z_max":0.02514,"peak_contact_force":7.3831,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2400.0,"raw_peak_contact_force":14.15002,"tcp_end":[0.44625,-0.00288,0.02168],"tcp_start":[0.4489,0.04564,0.03445],"tcp_to_object_dist_end":0.03736,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":783.0,"n_steps_budget":870.0,"object_pos_end":[0.45226,-0.13681,0.02497],"object_pos_start":[0.45169,-0.03969,0.02499],"object_to_goal_dist_end":0.04952,"object_to_goal_dist_start":0.12042,"object_z_max":0.02982,"peak_contact_force":0.4349,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2179.0,"raw_peak_contact_force":58.55007,"tcp_end":[0.49325,-0.12496,0.01985],"tcp_start":[0.44625,-0.00288,0.02168],"tcp_to_object_dist_end":0.04297,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45156,-0.13756,0.02499],"object_pos_start":[0.45226,-0.13681,0.02497],"object_to_goal_dist_end":0.05002,"object_to_goal_dist_start":0.04952,"object_z_max":0.02511,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3983.0,"raw_peak_contact_force":11.98853,"tcp_end":[0.49329,0.02754,0.08732],"tcp_start":[0.49325,-0.12496,0.01985],"tcp_to_object_dist_end":0.18134,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.78659,"average_solve_count":164.0,"average_success_count":164.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.0834,"contact_1.speed":0.04659,"push_1.push_depth":0.09998},"optimized_scores":{"best_composite_score":0.45596,"best_fitness_score":0.66596,"best_task_score":0.66847},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":824.0,"contact_point_centroid":[0.56136,-0.04654,0.05407],"force_p95":119.51331,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":137.36156,"mean_force":78.30567,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52712,-0.03085,0.02366]},{"body_a":"world","body_b":"push_box","contact_count":1586.0,"contact_point_centroid":[0.55616,-0.08045,-0.00035],"force_p95":88.31107,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":102.14246,"mean_force":52.00181,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52668,-0.03251,0.02389]},{"body_a":"attachment","body_b":"push_box","contact_count":830.0,"contact_point_centroid":[0.54659,-0.03896,0.05443],"force_p95":83.35283,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":91.91514,"mean_force":50.35444,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52729,-0.03039,0.02363]},{"body_a":"world","body_b":"push_box","contact_count":3665.0,"contact_point_centroid":[0.53437,-0.10885,-3e-05],"force_p95":0.2775,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":82.59991,"mean_force":0.50314,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5027,-0.00749,0.06651]},{"body_a":"push_box","body_b":"link7","contact_count":52.0,"contact_point_centroid":[0.54974,-0.09716,0.05731],"force_p95":66.85022,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":76.39377,"mean_force":27.19496,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50875,-0.08666,0.03078]},{"body_a":"attachment","body_b":"push_box","contact_count":63.0,"contact_point_centroid":[0.53312,-0.0887,0.06138],"force_p95":47.08161,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":67.08139,"mean_force":17.03604,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50821,-0.08432,0.03132]},{"body_a":"attachment","body_b":"push_box","contact_count":118.0,"contact_point_centroid":[0.55449,0.02226,0.03954],"force_p95":7.33191,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.66888,"mean_force":2.77441,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54763,0.03421,0.02021]},{"body_a":"world","body_b":"push_box","contact_count":2214.0,"contact_point_centroid":[0.55324,-0.00087,-1e-05],"force_p95":1.1111,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.95304,"mean_force":0.40261,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5452,0.05541,0.02317]},{"body_a":"world","body_b":"push_box","contact_count":3880.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5223,0.03844,0.16447]}],"total_contact_groups":9},"final_pose_error":0.10206,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53379,-0.10893,0.02499],"final_tcp_position":[0.50006,0.06067,0.10064],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":137.36156,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":970.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3880.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.5466,0.07724,0.03104],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0764,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.55496,-0.00711,0.02509],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.1531,"object_to_goal_dist_start":0.16043,"object_z_max":0.02518,"peak_contact_force":5.75801,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2332.0,"raw_peak_contact_force":9.66888,"tcp_end":[0.54823,0.02967,0.01967],"tcp_start":[0.5466,0.07724,0.03104],"tcp_to_object_dist_end":0.03778,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":835.0,"n_steps_budget":930.0,"object_pos_end":[0.54009,-0.11675,0.03116],"object_pos_start":[0.55496,-0.00711,0.02509],"object_to_goal_dist_end":0.05245,"object_to_goal_dist_start":0.1531,"object_z_max":0.03117,"peak_contact_force":118.09871,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3240.0,"raw_peak_contact_force":137.36156,"tcp_end":[0.50997,-0.09092,0.02974],"tcp_start":[0.54823,0.02967,0.01967],"tcp_to_object_dist_end":0.03971,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53379,-0.10893,0.02499],"object_pos_start":[0.54009,-0.11675,0.03116],"object_to_goal_dist_end":0.05319,"object_to_goal_dist_start":0.05245,"object_z_max":0.03485,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3780.0,"raw_peak_contact_force":82.59991,"tcp_end":[0.50006,0.06067,0.10064],"tcp_start":[0.50997,-0.09092,0.02974],"tcp_to_object_dist_end":0.18874,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.65089,"average_solve_count":169.0,"average_success_count":169.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.09258,"contact_1.speed":0.02915,"push_1.push_depth":0.09923},"optimized_scores":{"best_composite_score":0.36704,"best_fitness_score":0.57704,"best_task_score":0.62396},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":772.0,"contact_point_centroid":[0.54939,-0.01125,0.05482],"force_p95":114.91666,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":129.77072,"mean_force":76.65854,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51825,0.00444,0.0235]},{"body_a":"attachment","body_b":"push_box","contact_count":769.0,"contact_point_centroid":[0.53685,-0.00455,0.05197],"force_p95":102.42304,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":108.82795,"mean_force":57.60369,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51821,0.00423,0.02352]},{"body_a":"world","body_b":"push_box","contact_count":1473.0,"contact_point_centroid":[0.54395,-0.04719,-0.00031],"force_p95":80.02497,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":94.46936,"mean_force":52.21182,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51793,0.0025,0.02373]},{"body_a":"push_box","body_b":"link7","contact_count":44.0,"contact_point_centroid":[0.54919,-0.06183,0.05585],"force_p95":84.38527,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":93.0755,"mean_force":39.56008,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50688,-0.05191,0.03023]},{"body_a":"attachment","body_b":"push_box","contact_count":61.0,"contact_point_centroid":[0.52898,-0.05496,0.06007],"force_p95":63.43057,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":83.36875,"mean_force":23.11046,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50616,-0.04896,0.03116]},{"body_a":"world","body_b":"push_box","contact_count":3699.0,"contact_point_centroid":[0.52526,-0.08271,-3e-05],"force_p95":0.25226,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":83.31521,"mean_force":0.49016,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50099,0.02391,0.07088]},{"body_a":"attachment","body_b":"push_box","contact_count":218.0,"contact_point_centroid":[0.53814,0.05709,0.03792],"force_p95":5.12014,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.59128,"mean_force":2.2557,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5313,0.06905,0.02036]},{"body_a":"world","body_b":"push_box","contact_count":3288.0,"contact_point_centroid":[0.53667,0.03411,-1e-05],"force_p95":1.85153,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.69707,"mean_force":0.40374,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5292,0.08892,0.0229]},{"body_a":"world","body_b":"push_box","contact_count":3996.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51453,0.05559,0.1638]}],"total_contact_groups":9},"final_pose_error":0.07248,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52463,-0.08273,0.02499],"final_tcp_position":[0.49874,0.08972,0.10978],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":129.77072,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":999.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.53088,0.11131,0.03067],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07479,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":953.0,"n_steps_budget":1000.0,"object_pos_end":[0.53974,0.02707,0.02504],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.18147,"object_to_goal_dist_start":0.1905,"object_z_max":0.02513,"peak_contact_force":4.09057,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3506.0,"raw_peak_contact_force":7.59128,"tcp_end":[0.5319,0.06391,0.01977],"tcp_start":[0.53088,0.11131,0.03067],"tcp_to_object_dist_end":0.03804,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":779.0,"n_steps_budget":870.0,"object_pos_end":[0.53321,-0.08425,0.03137],"object_pos_start":[0.53974,0.02707,0.02504],"object_to_goal_dist_end":0.07393,"object_to_goal_dist_start":0.18147,"object_z_max":0.03136,"peak_contact_force":114.9923,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3014.0,"raw_peak_contact_force":129.77072,"tcp_end":[0.50773,-0.0551,0.02897],"tcp_start":[0.5319,0.06391,0.01977],"tcp_to_object_dist_end":0.03879,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52463,-0.08273,0.02499],"object_pos_start":[0.53321,-0.08425,0.03137],"object_to_goal_dist_end":0.07164,"object_to_goal_dist_start":0.07393,"object_z_max":0.03481,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3804.0,"raw_peak_contact_force":93.0755,"tcp_end":[0.49874,0.08972,0.10978],"tcp_start":[0.50773,-0.0551,0.02897],"tcp_to_object_dist_end":0.19391,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```