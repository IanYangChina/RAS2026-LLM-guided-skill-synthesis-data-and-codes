## Search State

- **Seed**: 4
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | 0.3677 | 0.78 | ❌ rejected |
| 12 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | time_limit | pose_tolerance | 4 | -0.0820 | 0.00 | ❌ rejected |
| 11 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.4171 | 0.80 | ❌ rejected |
| 10 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.1931 | 0.38 | ❌ rejected |
| 9 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.3961 | 0.36 | ❌ rejected |

**Proposal policy**: task_score is 0.78 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.368) — your mutation base

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

- **Composite score**: 0.368
- **task_score** (E): 0.782
- **fitness_score**: 0.728  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1868 |
| descend_1 | 1.00 | 1.00 | 0.1118 |
| push_1 | 1.00 | 1.00 | 0.1473 |
| retract_1 | 1.00 | 1.00 | 0.1150 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.547, 0.066, 0.138) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_1 | descend | 1.00 / step_budget | (0.547, 0.066, 0.138)→(0.539, 0.030, 0.033) | (0.531, 0.007, 0.025)→(0.533, -0.004, 0.026) | 0.161→0.150 | 1.00 / 3.333 | 75.557 | 178.879 |
| push_1 | push | 1.00 / time_limit | (0.539, 0.030, 0.033)→(0.504, -0.111, 0.023) | (0.533, -0.004, 0.026)→(0.513, -0.116, 0.025) | 0.150→0.037 | 1.00 / 3.000 | 0.905 | 70.619 |
| retract_1 | retract | 1.00 / step_budget | (0.504, -0.111, 0.023)→(0.497, -0.147, 0.132) | (0.513, -0.116, 0.025)→(0.511, -0.118, 0.025) | 0.037→0.036 | 1.00 / 4.000 | 0.245 | 1.757 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.828
- goal_progress: 0.987
- terminal_score: 0.987
- phase_score: 0.845
- phase_breakdown.pre_push_score: 0.516
- phase_breakdown.push_to_goal_score: 0.986

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.902
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.987
- **Median Q (composite search score)**: 0.486
- **K-run variance**: 0.0432
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.372


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.57746,"average_solve_count":142.0,"average_success_count":142.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.09812,"approach_1.arc_height":0.07815,"descend_1.descend_speed":0.05793,"push_1.push_distance":0.23955,"push_1.push_speed":0.09667,"retract_1.retract_speed":0.16918},"optimized_scores":{"best_composite_score":0.07571,"best_fitness_score":0.43571,"best_task_score":0.42519},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":273.0,"contact_point_centroid":[0.57906,0.02326,0.0463],"force_p95":209.86016,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":211.43068,"mean_force":148.84735,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.56921,0.02842,0.04771]},{"body_a":"world","body_b":"push_box","contact_count":2502.0,"contact_point_centroid":[0.55803,0.00122,-0.00016],"force_p95":147.39909,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":173.56418,"mean_force":16.60577,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.57328,0.04313,0.08901]},{"body_a":"attachment","body_b":"push_box","contact_count":787.0,"contact_point_centroid":[0.56621,-0.02325,0.04612],"force_p95":158.48299,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":159.81317,"mean_force":120.18008,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.56029,-0.02741,0.04625]},{"body_a":"world","body_b":"push_box","contact_count":2757.0,"contact_point_centroid":[0.5435,-0.03193,-0.00035],"force_p95":103.89606,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":135.01767,"mean_force":34.77292,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.55044,-0.04482,0.0422]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.56363,0.04559,0.25224]},{"body_a":"world","body_b":"push_box","contact_count":2284.0,"contact_point_centroid":[0.52641,-0.06165,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50252,-0.13257,0.07364]}],"total_contact_groups":6},"final_pose_error":0.01384,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52641,-0.06165,0.02499],"final_tcp_position":[0.49759,-0.14719,0.13166],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":211.43068,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_push","tcp_end":[0.58825,0.0633,0.15287],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.14636,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":749.0,"n_steps_budget":1000.0,"object_pos_end":[0.55754,-0.00359,0.02808],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.15734,"object_to_goal_dist_start":0.16043,"object_z_max":0.02827,"peak_contact_force":208.93915,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2775.0,"raw_peak_contact_force":211.43068,"subtask_id":"pre_push","tcp_end":[0.57671,0.0247,0.04408],"tcp_start":[0.58825,0.0633,0.15287],"tcp_to_object_dist_end":0.03773,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52641,-0.06165,0.02499],"object_pos_start":[0.55754,-0.00359,0.02808],"object_to_goal_dist_end":0.09221,"object_to_goal_dist_start":0.15734,"object_z_max":0.03567,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3544.0,"raw_peak_contact_force":159.81317,"subtask_id":"push_to_goal","tcp_end":[0.51054,-0.12022,0.02676],"tcp_start":[0.57671,0.0247,0.04408],"tcp_to_object_dist_end":0.0607,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":571.0,"n_steps_budget":600.0,"object_pos_end":[0.52641,-0.06165,0.02499],"object_pos_start":[0.52641,-0.06165,0.02499],"object_to_goal_dist_end":0.09221,"object_to_goal_dist_start":0.09221,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2284.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49759,-0.14719,0.13166],"tcp_start":[0.51054,-0.12022,0.02676],"tcp_to_object_dist_end":0.13974,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.17318,"average_solve_count":179.0,"average_success_count":179.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.19683,"approach_1.arc_height":0.09993,"descend_1.descend_speed":0.02282,"push_1.push_distance":0.22233,"push_1.push_speed":0.0998,"retract_1.retract_speed":0.18889},"optimized_scores":{"best_composite_score":0.48571,"best_fitness_score":0.84571,"best_task_score":0.93206},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":279.0,"contact_point_centroid":[0.54891,0.0587,0.0455],"force_p95":130.44372,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":140.4548,"mean_force":86.782,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.54267,0.06732,0.04692]},{"body_a":"world","body_b":"push_box","contact_count":2851.0,"contact_point_centroid":[0.5382,0.03699,-0.00011],"force_p95":70.17884,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":97.43598,"mean_force":8.79419,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5426,0.07696,0.074]},{"body_a":"attachment","body_b":"push_box","contact_count":850.0,"contact_point_centroid":[0.52171,-0.03226,0.02862],"force_p95":18.1463,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.05484,"mean_force":4.65641,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51877,-0.02038,0.02164]},{"body_a":"world","body_b":"push_box","contact_count":1689.0,"contact_point_centroid":[0.51994,-0.05846,-6e-05],"force_p95":8.42637,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.11345,"mean_force":2.65869,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52001,-0.0141,0.0218]},{"body_a":"push_box","body_b":"link7","contact_count":31.0,"contact_point_centroid":[0.53771,-0.102,0.05078],"force_p95":2.23862,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.26644,"mean_force":1.15562,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50606,-0.08953,0.02096]},{"body_a":"world","body_b":"push_box","contact_count":1742.0,"contact_point_centroid":[0.50944,-0.14603,-7e-05],"force_p95":0.57608,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.59271,"mean_force":0.31803,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49869,-0.12484,0.07875]},{"body_a":"attachment","body_b":"push_box","contact_count":128.0,"contact_point_centroid":[0.50206,-0.12039,0.03977],"force_p95":1.34083,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.51789,"mean_force":0.65601,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49981,-0.10852,0.03791]},{"body_a":"world","body_b":"push_box","contact_count":2524.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.54414,0.08523,0.24786]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.53633,-0.11179,0.05043],"force_p95":0.21308,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21308,"mean_force":0.21308,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50413,-0.10051,0.02092]}],"total_contact_groups":9},"final_pose_error":0.01431,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50839,-0.14014,0.02499],"final_tcp_position":[0.49714,-0.14596,0.13157],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":140.4548,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":631.0,"n_steps_budget":660.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2524.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_push","tcp_end":[0.54918,0.09692,0.1312],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12262,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":797.0,"n_steps_budget":1000.0,"object_pos_end":[0.53413,0.02316,0.02482],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.17649,"object_to_goal_dist_start":0.1905,"object_z_max":0.0254,"peak_contact_force":17.17986,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3130.0,"raw_peak_contact_force":140.4548,"subtask_id":"pre_push","tcp_end":[0.53752,0.05986,0.02731],"tcp_start":[0.54918,0.09692,0.1312],"tcp_to_object_dist_end":0.03694,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51187,-0.1372,0.02533],"object_pos_start":[0.53413,0.02316,0.02482],"object_to_goal_dist_end":0.01746,"object_to_goal_dist_start":0.17649,"object_z_max":0.02565,"peak_contact_force":0.37758,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2570.0,"raw_peak_contact_force":28.05484,"subtask_id":"push_to_goal","tcp_end":[0.50413,-0.10051,0.02092],"tcp_start":[0.53752,0.05986,0.02731],"tcp_to_object_dist_end":0.03776,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":571.0,"n_steps_budget":600.0,"object_pos_end":[0.50839,-0.14014,0.02499],"object_pos_start":[0.51187,-0.1372,0.02533],"object_to_goal_dist_end":0.01294,"object_to_goal_dist_start":0.01746,"object_z_max":0.03031,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1871.0,"raw_peak_contact_force":2.59271,"tcp_end":[0.49714,-0.14596,0.13157],"tcp_start":[0.50413,-0.10051,0.02092],"tcp_to_object_dist_end":0.10733,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.7438,"average_solve_count":121.0,"average_success_count":121.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.1624,"approach_1.arc_height":0.04695,"descend_1.descend_speed":0.05653,"push_1.push_distance":0.12529,"push_1.push_speed":0.07312,"retract_1.retract_speed":0.13524},"optimized_scores":{"best_composite_score":0.54174,"best_fitness_score":0.90174,"best_task_score":0.98726},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":213.0,"contact_point_centroid":[0.51007,0.00184,0.04612],"force_p95":158.12607,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":184.75218,"mean_force":81.59823,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50392,0.01107,0.04513]},{"body_a":"world","body_b":"push_box","contact_count":2785.0,"contact_point_centroid":[0.50588,-0.02017,-7e-05],"force_p95":41.32508,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":118.55603,"mean_force":6.51764,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50127,0.02098,0.07604]},{"body_a":"attachment","body_b":"push_box","contact_count":864.0,"contact_point_centroid":[0.50713,-0.06591,0.04172],"force_p95":14.50938,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.98786,"mean_force":4.93148,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49696,-0.05398,0.02134]},{"body_a":"world","body_b":"push_box","contact_count":1430.0,"contact_point_centroid":[0.50427,-0.10804,-5e-05],"force_p95":10.07558,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.25471,"mean_force":3.7548,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49707,-0.05248,0.02146]},{"body_a":"push_box","body_b":"link7","contact_count":211.0,"contact_point_centroid":[0.52833,-0.07587,0.05053],"force_p95":9.40483,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.49435,"mean_force":3.13339,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49677,-0.05999,0.02113]},{"body_a":"world","body_b":"push_box","contact_count":1778.0,"contact_point_centroid":[0.49958,-0.15805,-5e-05],"force_p95":0.54319,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.43215,"mean_force":0.3312,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49483,-0.13198,0.08181]},{"body_a":"attachment","body_b":"push_box","contact_count":163.0,"contact_point_centroid":[0.49868,-0.12956,0.04129],"force_p95":1.53683,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.25513,"mean_force":0.71568,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49371,-0.11766,0.03386]},{"body_a":"world","body_b":"push_box","contact_count":2644.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50019,0.04327,0.22299]}],"total_contact_groups":8},"final_pose_error":0.01411,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49855,-0.15084,0.02499],"final_tcp_position":[0.49661,-0.14682,0.13168],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":184.75218,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":661.0,"n_steps_budget":690.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2644.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_push","tcp_end":[0.50262,0.03805,0.12948],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11898,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":757.0,"n_steps_budget":1000.0,"object_pos_end":[0.50624,-0.03293,0.02492],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.11723,"object_to_goal_dist_start":0.13127,"object_z_max":0.02535,"peak_contact_force":0.55219,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2998.0,"raw_peak_contact_force":184.75218,"subtask_id":"pre_push","tcp_end":[0.5016,0.00419,0.02643],"tcp_start":[0.50262,0.03805,0.12948],"tcp_to_object_dist_end":0.03744,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50163,-0.14975,0.02539],"object_pos_start":[0.50624,-0.03293,0.02492],"object_to_goal_dist_end":0.0017,"object_to_goal_dist_start":0.11723,"object_z_max":0.02581,"peak_contact_force":2.09336,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2505.0,"raw_peak_contact_force":23.98786,"subtask_id":"push_to_goal","tcp_end":[0.49635,-0.11315,0.02067],"tcp_start":[0.5016,0.00419,0.02643],"tcp_to_object_dist_end":0.03729,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":601.0,"n_steps_budget":630.0,"object_pos_end":[0.49855,-0.15084,0.02499],"object_pos_start":[0.50163,-0.14975,0.02539],"object_to_goal_dist_end":0.00167,"object_to_goal_dist_start":0.0017,"object_z_max":0.02949,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1941.0,"raw_peak_contact_force":2.43215,"tcp_end":[0.49661,-0.14682,0.13168],"tcp_start":[0.49635,-0.11315,0.02067],"tcp_to_object_dist_end":0.10679,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```