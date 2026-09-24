## Search State

- **Seed**: 4
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.3227 | 0.73 | ❌ rejected |
| 6 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.3482 | 0.75 | ✅ accepted |
| 5 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 9 | -0.1577 | 0.00 | ❌ rejected |
| 4 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.1422 | 0.00 | ❌ rejected |
| 3 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.3415 | 0.74 | ❌ rejected |

**Proposal policy**: task_score is 0.73 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.750, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.323) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: force_threshold_switch
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
  control: impedance_control
  termination: contact_detected
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
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
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1

```

## Design Metrics

- **Composite score**: 0.323
- **task_score** (E): 0.728
- **fitness_score**: 0.683  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2838 |
| contact_1 | 1.00 | 1.00 | 0.0480 |
| push_1 | 1.00 | 1.00 | 0.1196 |
| retract_1 | 0.00 | 1.00 | 0.1339 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.526, 0.082, 0.032) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.526, 0.082, 0.032)→(0.527, 0.036, 0.020) | (0.531, 0.007, 0.025)→(0.533, -0.001, 0.025) | 0.161→0.153 | 1.00 / 2.000 | 2.626 | 12.950 |
| push_1 | push | 1.00 / step_budget | (0.527, 0.036, 0.020)→(0.504, -0.081, 0.025) | (0.533, -0.001, 0.025)→(0.520, -0.114, 0.029) | 0.153→0.045 | 1.00 / 3.667 | 70.343 | 90.184 |
| retract_1 | retract | 0.00 / step_budget | (0.504, -0.081, 0.025)→(0.498, 0.039, 0.086) | (0.520, -0.114, 0.029)→(0.518, -0.110, 0.025) | 0.045→0.047 | 1.00 / 4.000 | 0.245 | 64.466 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.483
- goal_progress: 0.960
- terminal_score: 0.960
- phase_score: 0.840
- phase_breakdown.push_score: 0.836
- phase_breakdown.approach_score: 0.821
- phase_breakdown.contact_score: 0.860

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.888
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.960
- **Median Q (composite search score)**: 0.224
- **K-run variance**: 0.0211
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Parameters at upper bound**: push_1.push_depth
- **Final σ (mean)**: 0.337


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.41053,"average_solve_count":190.0,"average_success_count":190.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.0878,"contact_1.contact_force":8.55563,"push_1.push_depth":0.07737,"push_1.push_distance":0.06153,"push_1.push_speed":0.06212,"retract_1.speed":0.04351},"optimized_scores":{"best_composite_score":0.22428,"best_fitness_score":0.58428,"best_task_score":0.59972},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":989.0,"contact_point_centroid":[0.56139,-0.04123,0.05297],"force_p95":105.23967,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":111.43313,"mean_force":69.45776,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52574,-0.0217,0.0233]},{"body_a":"world","body_b":"push_box","contact_count":3701.0,"contact_point_centroid":[0.53077,-0.09357,-3e-05],"force_p95":0.24897,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":89.23952,"mean_force":0.48378,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50297,-0.00658,0.05788]},{"body_a":"world","body_b":"push_box","contact_count":1963.0,"contact_point_centroid":[0.55224,-0.0742,-0.00034],"force_p95":65.10031,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":78.23885,"mean_force":42.98556,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52564,-0.02202,0.02335]},{"body_a":"push_box","body_b":"link7","contact_count":47.0,"contact_point_centroid":[0.54992,-0.07646,0.05567],"force_p95":69.01587,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":76.33973,"mean_force":30.43014,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50857,-0.06462,0.02948]},{"body_a":"attachment","body_b":"push_box","contact_count":994.0,"contact_point_centroid":[0.54586,-0.03075,0.05625],"force_p95":62.32108,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":65.25409,"mean_force":39.2576,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52586,-0.02144,0.02328]},{"body_a":"attachment","body_b":"push_box","contact_count":63.0,"contact_point_centroid":[0.53208,-0.06875,0.0601],"force_p95":47.01822,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":57.01358,"mean_force":17.43803,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5079,-0.06236,0.02999]},{"body_a":"attachment","body_b":"push_box","contact_count":91.0,"contact_point_centroid":[0.55369,0.02254,0.03744],"force_p95":10.35611,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.87964,"mean_force":3.11342,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5476,0.03448,0.02025]},{"body_a":"world","body_b":"push_box","contact_count":1882.0,"contact_point_centroid":[0.55325,-0.00042,-1e-05],"force_p95":1.01845,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.37026,"mean_force":0.40189,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54519,0.056,0.02334]},{"body_a":"world","body_b":"push_box","contact_count":3860.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52231,0.03845,0.16443]}],"total_contact_groups":9},"final_pose_error":0.12598,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53024,-0.09335,0.02499],"final_tcp_position":[0.50096,0.04206,0.08506],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":111.43313,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":965.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3860.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.54659,0.07723,0.03107],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0764,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":529.0,"n_steps_budget":600.0,"object_pos_end":[0.55447,-0.00634,0.02517],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.15364,"object_to_goal_dist_start":0.16043,"object_z_max":0.02518,"peak_contact_force":0.0,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1973.0,"raw_peak_contact_force":11.87964,"tcp_end":[0.54816,0.03041,0.01978],"tcp_start":[0.54659,0.07723,0.03107],"tcp_to_object_dist_end":0.03767,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53471,-0.09851,0.03075],"object_pos_start":[0.55447,-0.00634,0.02517],"object_to_goal_dist_end":0.06236,"object_to_goal_dist_start":0.15364,"object_z_max":0.03075,"peak_contact_force":106.33771,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3946.0,"raw_peak_contact_force":111.43313,"tcp_end":[0.50957,-0.06754,0.02876],"tcp_start":[0.54816,0.03041,0.01978],"tcp_to_object_dist_end":0.03994,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53024,-0.09335,0.02499],"object_pos_start":[0.53471,-0.09851,0.03075],"object_to_goal_dist_end":0.06421,"object_to_goal_dist_start":0.06236,"object_z_max":0.03297,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3811.0,"raw_peak_contact_force":89.23952,"tcp_end":[0.50096,0.04206,0.08506],"tcp_start":[0.50957,-0.06754,0.02876],"tcp_to_object_dist_end":0.151,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.79874,"average_solve_count":159.0,"average_success_count":159.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.0944,"contact_1.contact_force":11.82605,"push_1.push_depth":0.09833,"push_1.push_distance":0.04608,"push_1.push_speed":0.08449,"retract_1.speed":0.0766},"optimized_scores":{"best_composite_score":0.21555,"best_fitness_score":0.57555,"best_task_score":0.62464},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":885.0,"contact_point_centroid":[0.5456,-0.01312,0.05485],"force_p95":95.77262,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":102.35638,"mean_force":63.75386,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51668,0.00321,0.02275]},{"body_a":"attachment","body_b":"push_box","contact_count":887.0,"contact_point_centroid":[0.53548,-0.00617,0.05271],"force_p95":83.11105,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":93.03317,"mean_force":48.75037,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51672,0.00337,0.02275]},{"body_a":"world","body_b":"push_box","contact_count":3710.0,"contact_point_centroid":[0.52301,-0.08224,-3e-05],"force_p95":0.25041,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":84.81463,"mean_force":0.46286,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50003,0.01207,0.06285]},{"body_a":"push_box","body_b":"link7","contact_count":45.0,"contact_point_centroid":[0.54344,-0.06918,0.05554],"force_p95":74.50774,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":81.97295,"mean_force":37.82869,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5048,-0.05214,0.02842]},{"body_a":"attachment","body_b":"push_box","contact_count":59.0,"contact_point_centroid":[0.52791,-0.05763,0.05975],"force_p95":57.54119,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":75.37211,"mean_force":23.24126,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50429,-0.05019,0.02897]},{"body_a":"world","body_b":"push_box","contact_count":1725.0,"contact_point_centroid":[0.53808,-0.04934,-0.00027],"force_p95":62.93021,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":73.07612,"mean_force":42.80594,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51661,0.00249,0.02287]},{"body_a":"attachment","body_b":"push_box","contact_count":99.0,"contact_point_centroid":[0.53803,0.05797,0.03797],"force_p95":8.17158,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.75895,"mean_force":3.16046,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53121,0.06991,0.0205]},{"body_a":"world","body_b":"push_box","contact_count":1839.0,"contact_point_centroid":[0.5367,0.03491,-1e-05],"force_p95":1.1402,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.08861,"mean_force":0.42407,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52922,0.09041,0.02342]},{"body_a":"world","body_b":"push_box","contact_count":3988.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51452,0.05554,0.16393]}],"total_contact_groups":9},"final_pose_error":0.10009,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5225,-0.08213,0.02499],"final_tcp_position":[0.49869,0.06622,0.09525],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":102.35638,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":997.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3988.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.53087,0.11123,0.03085],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07473,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":523.0,"n_steps_budget":600.0,"object_pos_end":[0.53833,0.02883,0.02512],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.1829,"object_to_goal_dist_start":0.1905,"object_z_max":0.02518,"peak_contact_force":6.27958,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1938.0,"raw_peak_contact_force":12.75895,"tcp_end":[0.53174,0.06562,0.02002],"tcp_start":[0.53087,0.11123,0.03085],"tcp_to_object_dist_end":0.03772,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":899.0,"n_steps_budget":1000.0,"object_pos_end":[0.52586,-0.08845,0.03077],"object_pos_start":[0.53833,0.02883,0.02512],"object_to_goal_dist_end":0.06702,"object_to_goal_dist_start":0.1829,"object_z_max":0.03078,"peak_contact_force":94.9736,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3497.0,"raw_peak_contact_force":102.35638,"tcp_end":[0.50575,-0.05504,0.02747],"tcp_start":[0.53174,0.06562,0.02002],"tcp_to_object_dist_end":0.03913,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5225,-0.08213,0.02499],"object_pos_start":[0.52586,-0.08845,0.03077],"object_to_goal_dist_end":0.07151,"object_to_goal_dist_start":0.06702,"object_z_max":0.03167,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3814.0,"raw_peak_contact_force":84.81463,"tcp_end":[0.49869,0.06622,0.09525],"tcp_start":[0.50575,-0.05504,0.02747],"tcp_to_object_dist_end":0.16587,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.06696,"average_solve_count":224.0,"average_success_count":224.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.05391,"contact_1.contact_force":16.49704,"push_1.push_depth":0.1,"push_1.push_distance":0.0239,"push_1.push_speed":0.0571,"retract_1.speed":0.06262},"optimized_scores":{"best_composite_score":0.52814,"best_fitness_score":0.88814,"best_task_score":0.95991},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1444.0,"contact_point_centroid":[0.50932,-0.10756,-0.00012],"force_p95":49.07931,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":56.76292,"mean_force":20.33154,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49783,-0.05207,0.01984]},{"body_a":"push_box","body_b":"link7","contact_count":677.0,"contact_point_centroid":[0.52472,-0.05346,0.05225],"force_p95":40.75452,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":47.83283,"mean_force":28.80148,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49846,-0.03261,0.01991]},{"body_a":"attachment","body_b":"push_box","contact_count":933.0,"contact_point_centroid":[0.51257,-0.06138,0.04569],"force_p95":37.46669,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.44833,"mean_force":19.6986,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49782,-0.04998,0.01978]},{"body_a":"push_box","body_b":"link7","contact_count":57.0,"contact_point_centroid":[0.52479,-0.13833,0.05056],"force_p95":11.3516,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.34276,"mean_force":6.09428,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49391,-0.11261,0.02058]},{"body_a":"world","body_b":"push_box","contact_count":3799.0,"contact_point_centroid":[0.5008,-0.15434,-2e-05],"force_p95":0.32888,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.9617,"mean_force":0.35043,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49304,-0.05018,0.04831]},{"body_a":"attachment","body_b":"push_box","contact_count":84.0,"contact_point_centroid":[0.5059,0.00247,0.03411],"force_p95":13.15291,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.2102,"mean_force":3.7655,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49963,0.01433,0.02142]},{"body_a":"world","body_b":"push_box","contact_count":1921.0,"contact_point_centroid":[0.50484,-0.01976,-1e-05],"force_p95":0.97653,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.95353,"mean_force":0.41277,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4982,0.03566,0.02523]},{"body_a":"attachment","body_b":"push_box","contact_count":7.0,"contact_point_centroid":[0.50604,-0.13087,0.04147],"force_p95":0.40111,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.50661,"mean_force":0.11021,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4957,-0.119,0.01976]},{"body_a":"world","body_b":"push_box","contact_count":3800.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4992,0.02863,0.16606]}],"total_contact_groups":9},"final_pose_error":0.16003,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50089,-0.15519,0.02499],"final_tcp_position":[0.494,0.00798,0.07649],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":56.76292,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":950.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3800.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.50028,0.05778,0.03318],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07715,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":525.0,"n_steps_budget":600.0,"object_pos_end":[0.50586,-0.02637,0.02501],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.12377,"object_to_goal_dist_start":0.13127,"object_z_max":0.02513,"peak_contact_force":1.59699,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2005.0,"raw_peak_contact_force":14.2102,"tcp_end":[0.50001,0.01049,0.02083],"tcp_start":[0.50028,0.05778,0.03318],"tcp_to_object_dist_end":0.03755,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":986.0,"n_steps_budget":1000.0,"object_pos_end":[0.50076,-0.15572,0.02505],"object_pos_start":[0.50586,-0.02637,0.02501],"object_to_goal_dist_end":0.00577,"object_to_goal_dist_start":0.12377,"object_z_max":0.02771,"peak_contact_force":9.71867,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3054.0,"raw_peak_contact_force":56.76292,"tcp_end":[0.49589,-0.11895,0.01984],"tcp_start":[0.50001,0.01049,0.02083],"tcp_to_object_dist_end":0.03746,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50089,-0.15519,0.02499],"object_pos_start":[0.50076,-0.15572,0.02505],"object_to_goal_dist_end":0.00526,"object_to_goal_dist_start":0.00577,"object_z_max":0.02863,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3863.0,"raw_peak_contact_force":19.34276,"tcp_end":[0.494,0.00798,0.07649],"tcp_start":[0.49589,-0.11895,0.01984],"tcp_to_object_dist_end":0.17124,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```