## Search State

- **Seed**: 4
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6  | 0.4250 | 0.81 | ✅ accepted |
| 2 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6  | 0.0507 | 0.00 | ❌ rejected |
| 1 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | 5  | 0.4172 | 0.80 | ✅ accepted |
| 0 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6  | 0.4198 | 0.80 | ❌ rejected |

**Proposal policy**: task_score is 0.80 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702`
- Frozen object start: [0.5531667326686841, 0.0013593063377233885, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5531667326686841, 0.0013593063377233885, 0.025)
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
  frozen_object_start: [0.5532, 0.0014, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5531667326686841, 0.0013593063377233885, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0532, -0.1514, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.810, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.5531667326686841, 0.0013593063377233885, 0.025) | approach/contact targets near object start |
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

## Current Skill (Q=0.420) — your mutation base

```yaml
skill: push_to_goal
skill_type: arm_gripper
phases:
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
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
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
    lateral_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
- id: release_1
  type: release
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  end_effector_action: open
- id: insert_1
  type: insert
  generator: impedance_motion
  control: impedance_control
  termination: force_exceeded
  parameters:
    insertion_depth:
      type: scalar
      range:
      - 0.01
      - 0.15
    insertion_force:
      type: scalar
      range:
      - 1.0
      - 20.0

```

## Design Metrics

- **Composite score**: 0.420
- **task_score** (E): 0.797
- **fitness_score**: 0.447  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| push_1 | 1.00 | 1.00 | 0.1911 |
| align_1 | 1.00 | 1.00 | 0.1724 |
| release_1 | 0.33 | 1.00 | 0.1689 |
| insert_1 | 1.00 | 1.00 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| push_1 | push | 1.00 / time_limit | (0.500, -0.000, 0.301)→(0.496, -0.060, 0.120) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 | 1.00 / 4.000 | 0.245 | 0.245 |
| align_1 | align | 1.00 / step_budget | (0.496, -0.060, 0.120)→(0.527, 0.079, 0.027) | (0.531, 0.007, 0.025)→(0.534, 0.017, 0.028) | 0.161→0.171 | 1.00 / 3.667 | 24.668 | 62.643 |
| release_1 | release | 0.33 / step_budget | (0.527, 0.079, 0.027)→(0.504, -0.087, 0.020) | (0.534, 0.017, 0.028)→(0.522, -0.131, 0.025) | 0.171→0.035 | 1.00 / 4.333 | 22.463 | 105.352 |
| insert_1 | insert | 1.00 / force_exceeded | (0.504, -0.087, 0.020)→(0.504, -0.087, 0.020) | (0.522, -0.131, 0.025)→(0.522, -0.131, 0.025) | 0.035→0.035 | 1.00 / 4.333 | 40.847 | 40.847 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.694
- goal_progress: 0.935
- terminal_score: 0.935
- phase_score: 0.219
- phase_breakdown.push_score: 0.109
- phase_breakdown.approach_score: 0.821
- phase_breakdown.contact_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.505
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.935
- **Median Q (composite search score)**: 0.411
- **K-run variance**: 0.0020
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.361


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `8d5a7e825d9524a0954b44a69bda19e1d764760f64bb1262d03aec3c389fadbb`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `c4094dd933e0897d422d7ea261a82b80810f7dec183b19c1da5b940157e7d0c4`; realized-scene SHA-256: `721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.55317,0.00136,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.05317,-0.15136,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.55317,0.00136,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.68182,"average_solve_count":132.0,"average_success_count":132.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00979,"align_1.lateral_offset_y":-0.00557,"insert_1.insertion_depth":0.10225,"insert_1.insertion_force":13.78932,"push_1.push_distance":0.05427,"push_1.push_speed":0.06684},"optimized_scores":{"best_composite_score":0.41136,"best_fitness_score":0.43802,"best_task_score":0.78709},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":2152.0,"contact_point_centroid":[0.55609,-0.0532,-0.00016],"force_p95":57.33089,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":83.51877,"mean_force":20.66622,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52639,-0.00766,0.021]},{"body_a":"push_box","body_b":"link7","contact_count":1075.0,"contact_point_centroid":[0.56085,-0.04902,0.04961],"force_p95":54.82653,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":62.81613,"mean_force":35.20532,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52192,-0.0297,0.02122]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54501,-0.11347,0.04903],"force_p95":49.34238,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.34238,"mean_force":49.34238,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.5082,-0.09387,0.02086]},{"body_a":"attachment","body_b":"push_box","contact_count":863.0,"contact_point_centroid":[0.52809,-0.05634,0.03686],"force_p95":36.97771,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.87188,"mean_force":12.78016,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51879,-0.04567,0.02152]},{"body_a":"world","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.54888,-0.11848,-0.00029],"force_p95":29.73914,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.7719,"mean_force":29.44428,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.5082,-0.09387,0.02086]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.52993,-0.10217,0.04943],"force_p95":12.69043,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.69043,"mean_force":12.69043,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.5082,-0.09387,0.02086]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4972,-0.01761,0.20406]},{"body_a":"world","body_b":"push_box","contact_count":2824.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.52041,0.02139,0.06432]}],"total_contact_groups":8},"final_pose_error":0.05687,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53082,-0.13529,0.02475],"final_tcp_position":[0.50819,-0.09388,0.02085],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":83.51877,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.49641,-0.03524,0.1115],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10975,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":706.0,"n_steps_budget":990.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2824.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.54582,0.07487,0.02353],"tcp_start":[0.49641,-0.03524,0.1115],"tcp_to_object_dist_end":0.07389,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53082,-0.13528,0.02476],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.03416,"object_to_goal_dist_start":0.16043,"object_z_max":0.02904,"peak_contact_force":36.86745,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":4090.0,"raw_peak_contact_force":83.51877,"tcp_end":[0.5082,-0.09387,0.02086],"tcp_start":[0.54582,0.07487,0.02353],"tcp_to_object_dist_end":0.04735,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.53082,-0.13529,0.02475],"object_pos_start":[0.53082,-0.13528,0.02476],"object_to_goal_dist_end":0.03416,"object_to_goal_dist_start":0.03416,"object_z_max":0.02476,"peak_contact_force":49.34238,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4.0,"raw_peak_contact_force":49.34238,"tcp_end":[0.50819,-0.09388,0.02085],"tcp_start":[0.5082,-0.09387,0.02086],"tcp_to_object_dist_end":0.04735,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `452b4d03bf1b69f7d6475210c4cc0fbd85197208ecbf5594cd2cfcf54c82bcbb`; realized-scene SHA-256: `b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5366,0.03695,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.0366,-0.18695,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5366,0.03695,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90625,"average_solve_count":128.0,"average_success_count":128.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00181,"align_1.lateral_offset_y":-0.00989,"insert_1.insertion_depth":0.01301,"insert_1.insertion_force":19.99647,"push_1.push_distance":0.17053,"push_1.push_speed":0.09174},"optimized_scores":{"best_composite_score":0.36974,"best_fitness_score":0.39641,"best_task_score":0.67061},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":241.0,"contact_point_centroid":[0.53609,0.0697,0.04632],"force_p95":154.54192,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":187.43708,"mean_force":104.56971,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.52864,0.07686,0.04835]},{"body_a":"attachment","body_b":"push_box","contact_count":917.0,"contact_point_centroid":[0.53378,0.03006,0.03483],"force_p95":157.87021,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":166.85728,"mean_force":117.0588,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52956,0.04021,0.03562]},{"body_a":"world","body_b":"push_box","contact_count":3227.0,"contact_point_centroid":[0.53714,0.04081,-8e-05],"force_p95":64.40738,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":150.07027,"mean_force":8.75692,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51039,0.00241,0.08332]},{"body_a":"world","body_b":"push_box","contact_count":2445.0,"contact_point_centroid":[0.53845,-0.02345,-0.00042],"force_p95":106.5652,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":117.1559,"mean_force":59.61426,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5259,0.02331,0.03311]},{"body_a":"push_box","body_b":"link7","contact_count":1042.0,"contact_point_centroid":[0.56205,0.00049,0.06735],"force_p95":72.96261,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":86.28917,"mean_force":47.88421,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5283,0.03564,0.03456]},{"body_a":"push_box","body_b":"link7","contact_count":33.0,"contact_point_centroid":[0.56775,0.07394,0.06703],"force_p95":77.13594,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":77.19325,"mean_force":63.90464,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.53402,0.10646,0.0343]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.55341,-0.07222,0.0498],"force_p95":30.79225,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.79225,"mean_force":30.79225,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50999,-0.04931,0.02258]},{"body_a":"world","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.54444,-0.09022,-4e-05],"force_p95":19.65072,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.18185,"mean_force":10.64099,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50999,-0.04931,0.02258]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49727,-0.04009,0.21293]}],"total_contact_groups":9},"final_pose_error":0.10122,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53725,-0.09951,0.02494],"final_tcp_position":[0.50998,-0.0493,0.02256],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":187.43708,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.49658,-0.07929,0.13128],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.16252,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":938.0,"n_steps_budget":1000.0,"object_pos_end":[0.54285,0.06712,0.03275],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.22144,"object_to_goal_dist_start":0.1905,"object_z_max":0.03485,"peak_contact_force":73.51493,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":3501.0,"raw_peak_contact_force":187.43708,"tcp_end":[0.53515,0.11023,0.03206],"tcp_start":[0.49658,-0.07929,0.13128],"tcp_to_object_dist_end":0.0438,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53725,-0.09951,0.02495],"object_pos_start":[0.54285,0.06712,0.03275],"object_to_goal_dist_end":0.06275,"object_to_goal_dist_start":0.22144,"object_z_max":0.03447,"peak_contact_force":4.74746,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":4404.0,"raw_peak_contact_force":166.85728,"tcp_end":[0.50999,-0.04931,0.02258],"tcp_start":[0.53515,0.11023,0.03206],"tcp_to_object_dist_end":0.05718,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":660.0,"object_pos_end":[0.53725,-0.09951,0.02494],"object_pos_start":[0.53725,-0.09951,0.02495],"object_to_goal_dist_end":0.06275,"object_to_goal_dist_start":0.06275,"object_z_max":0.02495,"peak_contact_force":30.79225,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4.0,"raw_peak_contact_force":30.79225,"tcp_end":[0.50998,-0.0493,0.02256],"tcp_start":[0.50999,-0.04931,0.02258],"tcp_to_object_dist_end":0.05718,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e3aaa9b30183e782395a479a1824f41a69a2557638e862a63e7a5368dd2a464a`; realized-scene SHA-256: `5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50458,-0.01881,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.00458,-0.13119,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.50458,-0.01881,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89916,"average_solve_count":119.0,"average_success_count":119.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.0005,"align_1.lateral_offset_y":-0.00447,"insert_1.insertion_depth":0.05084,"insert_1.insertion_force":8.51255,"push_1.push_distance":0.08445,"push_1.push_speed":0.08756},"optimized_scores":{"best_composite_score":0.47845,"best_fitness_score":0.50512,"best_task_score":0.93454},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":2335.0,"contact_point_centroid":[0.50676,-0.09207,-0.0001],"force_p95":41.30537,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":65.67858,"mean_force":11.59764,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49656,-0.04044,0.02127]},{"body_a":"attachment","body_b":"push_box","contact_count":763.0,"contact_point_centroid":[0.51335,-0.06135,0.0476],"force_p95":48.26267,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":56.64298,"mean_force":21.97704,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.4974,-0.0503,0.02211]},{"body_a":"push_box","body_b":"link7","contact_count":760.0,"contact_point_centroid":[0.52417,-0.07253,0.05347],"force_p95":37.54792,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.39419,"mean_force":21.24817,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49711,-0.05191,0.02169]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.52293,-0.14582,0.04932],"force_p95":42.40643,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.40643,"mean_force":42.40643,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49462,-0.11928,0.01792]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.49838,-0.15857,-0.00012],"force_p95":23.43941,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.89852,"mean_force":10.86096,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49462,-0.11928,0.01792]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49723,-0.03324,0.20695]},{"body_a":"world","body_b":"push_box","contact_count":2384.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49678,-0.00637,0.07011]}],"total_contact_groups":7},"final_pose_error":0.03199,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49846,-0.15845,0.02476],"final_tcp_position":[0.49462,-0.11928,0.01791],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":65.67858,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.49649,-0.06604,0.1186],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10516,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":596.0,"n_steps_budget":990.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2384.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49984,0.0526,0.02602],"tcp_start":[0.49649,-0.06604,0.1186],"tcp_to_object_dist_end":0.07157,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49846,-0.15845,0.02476],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.00859,"object_to_goal_dist_start":0.13127,"object_z_max":0.02975,"peak_contact_force":25.77459,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":3858.0,"raw_peak_contact_force":65.67858,"tcp_end":[0.49462,-0.11928,0.01792],"tcp_start":[0.49984,0.0526,0.02602],"tcp_to_object_dist_end":0.03995,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.49846,-0.15845,0.02476],"object_pos_start":[0.49846,-0.15845,0.02476],"object_to_goal_dist_end":0.00859,"object_to_goal_dist_start":0.00859,"object_z_max":0.02476,"peak_contact_force":42.40643,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":5.0,"raw_peak_contact_force":42.40643,"tcp_end":[0.49462,-0.11928,0.01791],"tcp_start":[0.49462,-0.11928,0.01792],"tcp_to_object_dist_end":0.03995,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```