## Search State

- **Seed**: 4
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.3516 | 0.76 | ❌ rejected |
| 9 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.3486 | 0.76 | ✅ accepted |
| 8 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.3482 | 0.75 | ✅ accepted |
| 7 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.3227 | 0.73 | ❌ rejected |
| 6 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.3482 | 0.75 | ✅ accepted |

**Proposal policy**: task_score is 0.76 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.761, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.352) — your mutation base

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

- **Composite score**: 0.352
- **task_score** (E): 0.757
- **fitness_score**: 0.712  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2838 |
| contact_1 | 1.00 | 1.00 | 0.0480 |
| push_1 | 1.00 | 1.00 | 0.1268 |
| retract_1 | 0.00 | 1.00 | 0.1381 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.526, 0.082, 0.032) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.526, 0.082, 0.032)→(0.527, 0.035, 0.020) | (0.531, 0.007, 0.025)→(0.533, -0.001, 0.025) | 0.161→0.153 | 1.00 / 3.000 | 5.009 | 12.728 |
| push_1 | push | 1.00 / step_budget | (0.527, 0.035, 0.020)→(0.504, -0.088, 0.026) | (0.533, -0.001, 0.025)→(0.522, -0.120, 0.029) | 0.153→0.042 | 1.00 / 3.333 | 71.501 | 106.368 |
| retract_1 | retract | 0.00 / step_budget | (0.504, -0.088, 0.026)→(0.498, 0.036, 0.086) | (0.522, -0.120, 0.029)→(0.519, -0.117, 0.025) | 0.042→0.042 | 1.00 / 4.000 | 0.245 | 63.964 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.449
- goal_progress: 0.953
- terminal_score: 0.953
- phase_score: 0.839
- phase_breakdown.push_score: 0.834
- phase_breakdown.approach_score: 0.820
- phase_breakdown.contact_score: 0.860

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.885
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.953
- **Median Q (composite search score)**: 0.318
- **K-run variance**: 0.0168
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Parameters at upper bound**: push_1.push_depth
- **Final σ (mean)**: 0.493


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.6875,"average_solve_count":176.0,"average_success_count":176.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.08214,"contact_1.contact_force":4.2399,"push_1.push_depth":0.09854,"push_1.push_distance":0.12692,"push_1.push_speed":0.08107,"retract_1.speed":0.06623},"optimized_scores":{"best_composite_score":0.31758,"best_fitness_score":0.67758,"best_task_score":0.70049},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":963.0,"contact_point_centroid":[0.55845,-0.04829,0.05448],"force_p95":112.19913,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":130.36308,"mean_force":73.87309,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52591,-0.03222,0.02348]},{"body_a":"world","body_b":"push_box","contact_count":1960.0,"contact_point_centroid":[0.55129,-0.08061,-0.00033],"force_p95":77.09109,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":91.16848,"mean_force":46.30804,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52625,-0.0312,0.02339]},{"body_a":"world","body_b":"push_box","contact_count":3627.0,"contact_point_centroid":[0.53048,-0.11235,-3e-05],"force_p95":0.41923,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":83.55388,"mean_force":0.53377,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50234,-0.02002,0.0597]},{"body_a":"attachment","body_b":"push_box","contact_count":959.0,"contact_point_centroid":[0.54516,-0.04128,0.05472],"force_p95":79.48086,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":82.67955,"mean_force":50.11785,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52584,-0.03243,0.0235]},{"body_a":"push_box","body_b":"link7","contact_count":54.0,"contact_point_centroid":[0.55038,-0.09613,0.0559],"force_p95":74.40272,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":82.40112,"mean_force":30.87441,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50774,-0.08642,0.03023]},{"body_a":"attachment","body_b":"push_box","contact_count":75.0,"contact_point_centroid":[0.53115,-0.08871,0.06049],"force_p95":54.48758,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":68.53584,"mean_force":17.4296,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50698,-0.08331,0.03092]},{"body_a":"attachment","body_b":"push_box","contact_count":84.0,"contact_point_centroid":[0.55235,0.02257,0.03401],"force_p95":7.60467,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.9254,"mean_force":2.60917,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54755,0.03454,0.02024]},{"body_a":"world","body_b":"push_box","contact_count":1916.0,"contact_point_centroid":[0.5535,7e-05,-1e-05],"force_p95":0.90358,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.34253,"mean_force":0.36414,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54523,0.05554,0.02333]},{"body_a":"world","body_b":"push_box","contact_count":3884.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52229,0.03842,0.16451]}],"total_contact_groups":9},"final_pose_error":0.13164,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52982,-0.11232,0.02499],"final_tcp_position":[0.50047,0.03436,0.0871],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":130.36308,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":971.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3884.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.54658,0.0772,0.03117],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07638,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":529.0,"n_steps_budget":600.0,"object_pos_end":[0.55514,-0.00648,0.02495],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.15374,"object_to_goal_dist_start":0.16043,"object_z_max":0.02514,"peak_contact_force":7.16032,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2000.0,"raw_peak_contact_force":11.9254,"tcp_end":[0.54813,0.03033,0.01975],"tcp_start":[0.54658,0.0772,0.03117],"tcp_to_object_dist_end":0.03783,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":978.0,"n_steps_budget":1000.0,"object_pos_end":[0.53633,-0.11865,0.03105],"object_pos_start":[0.55514,-0.00648,0.02495],"object_to_goal_dist_end":0.04836,"object_to_goal_dist_start":0.15374,"object_z_max":0.03105,"peak_contact_force":108.48586,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3882.0,"raw_peak_contact_force":130.36308,"tcp_end":[0.50881,-0.09051,0.0292],"tcp_start":[0.54813,0.03033,0.01975],"tcp_to_object_dist_end":0.0394,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52982,-0.11232,0.02499],"object_pos_start":[0.53633,-0.11865,0.03105],"object_to_goal_dist_end":0.04805,"object_to_goal_dist_start":0.04836,"object_z_max":0.03487,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3756.0,"raw_peak_contact_force":83.55388,"tcp_end":[0.50047,0.03436,0.0871],"tcp_start":[0.50881,-0.09051,0.0292],"tcp_to_object_dist_end":0.16198,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.47541,"average_solve_count":183.0,"average_success_count":183.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.09524,"contact_1.contact_force":11.33538,"push_1.push_depth":0.1,"push_1.push_distance":0.18903,"push_1.push_speed":0.09191,"retract_1.speed":0.01015},"optimized_scores":{"best_composite_score":0.21263,"best_fitness_score":0.57263,"best_task_score":0.61664},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":846.0,"contact_point_centroid":[0.54768,-0.01222,0.05483],"force_p95":107.72294,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":118.93418,"mean_force":70.84648,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51743,0.00403,0.0232]},{"body_a":"attachment","body_b":"push_box","contact_count":849.0,"contact_point_centroid":[0.53612,-0.00489,0.05228],"force_p95":95.9638,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":101.34604,"mean_force":52.52669,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51749,0.00425,0.02319]},{"body_a":"push_box","body_b":"link7","contact_count":57.0,"contact_point_centroid":[0.54671,-0.06442,0.05573],"force_p95":85.67396,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":90.88581,"mean_force":40.37249,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50578,-0.05176,0.02956]},{"body_a":"world","body_b":"push_box","contact_count":3643.0,"contact_point_centroid":[0.5262,-0.08174,-3e-05],"force_p95":0.26785,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":88.49463,"mean_force":0.57953,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50088,0.0047,0.05914]},{"body_a":"attachment","body_b":"push_box","contact_count":74.0,"contact_point_centroid":[0.52915,-0.05599,0.06048],"force_p95":68.4026,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":83.89466,"mean_force":25.36496,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50518,-0.04954,0.03019]},{"body_a":"world","body_b":"push_box","contact_count":1623.0,"contact_point_centroid":[0.54123,-0.04864,-0.00029],"force_p95":70.44598,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":82.53715,"mean_force":47.79716,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51718,0.00235,0.02341]},{"body_a":"attachment","body_b":"push_box","contact_count":99.0,"contact_point_centroid":[0.53803,0.05797,0.03797],"force_p95":8.17158,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.75895,"mean_force":3.16046,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53121,0.06991,0.0205]},{"body_a":"world","body_b":"push_box","contact_count":1839.0,"contact_point_centroid":[0.5367,0.03491,-1e-05],"force_p95":1.1402,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.08861,"mean_force":0.42407,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52922,0.09041,0.02342]},{"body_a":"world","body_b":"push_box","contact_count":3988.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51452,0.05554,0.16393]}],"total_contact_groups":9},"final_pose_error":0.11766,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52558,-0.08159,0.02499],"final_tcp_position":[0.49948,0.05091,0.08656],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":118.93418,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":997.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3988.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.53087,0.11123,0.03085],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07473,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":523.0,"n_steps_budget":600.0,"object_pos_end":[0.53833,0.02883,0.02512],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.1829,"object_to_goal_dist_start":0.1905,"object_z_max":0.02518,"peak_contact_force":6.27958,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1938.0,"raw_peak_contact_force":12.75895,"tcp_end":[0.53174,0.06562,0.02002],"tcp_start":[0.53087,0.11123,0.03085],"tcp_to_object_dist_end":0.03772,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":858.0,"n_steps_budget":960.0,"object_pos_end":[0.53016,-0.08635,0.03111],"object_pos_start":[0.53833,0.02883,0.02512],"object_to_goal_dist_end":0.0707,"object_to_goal_dist_start":0.1829,"object_z_max":0.03111,"peak_contact_force":104.35967,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3318.0,"raw_peak_contact_force":118.93418,"tcp_end":[0.50675,-0.05536,0.02832],"tcp_start":[0.53174,0.06562,0.02002],"tcp_to_object_dist_end":0.03895,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52558,-0.08159,0.02499],"object_pos_start":[0.53016,-0.08635,0.03111],"object_to_goal_dist_end":0.07303,"object_to_goal_dist_start":0.0707,"object_z_max":0.03395,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3774.0,"raw_peak_contact_force":90.88581,"tcp_end":[0.49948,0.05091,0.08656],"tcp_start":[0.50675,-0.05536,0.02832],"tcp_to_object_dist_end":0.14843,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.30392,"average_solve_count":204.0,"average_success_count":204.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.05125,"contact_1.contact_force":14.86476,"push_1.push_depth":0.09994,"push_1.push_distance":0.17605,"push_1.push_speed":0.08096,"retract_1.speed":0.09202},"optimized_scores":{"best_composite_score":0.52472,"best_fitness_score":0.88472,"best_task_score":0.95309},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1225.0,"contact_point_centroid":[0.50834,-0.10689,-0.00013],"force_p95":54.85779,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":69.80636,"mean_force":20.38767,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4977,-0.05321,0.01977]},{"body_a":"push_box","body_b":"link7","contact_count":512.0,"contact_point_centroid":[0.52494,-0.04756,0.05236],"force_p95":44.45094,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":57.51801,"mean_force":32.11673,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49867,-0.02665,0.01999]},{"body_a":"attachment","body_b":"push_box","contact_count":809.0,"contact_point_centroid":[0.51088,-0.06149,0.04291],"force_p95":42.95796,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.75793,"mean_force":19.52064,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49776,-0.05006,0.01975]},{"body_a":"push_box","body_b":"link7","contact_count":39.0,"contact_point_centroid":[0.52526,-0.13729,0.05017],"force_p95":9.12827,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.45094,"mean_force":3.28389,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49366,-0.11176,0.02061]},{"body_a":"world","body_b":"push_box","contact_count":3828.0,"contact_point_centroid":[0.50069,-0.15558,-2e-05],"force_p95":0.33126,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.35628,"mean_force":0.29081,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49318,-0.04357,0.05147]},{"body_a":"attachment","body_b":"push_box","contact_count":83.0,"contact_point_centroid":[0.50549,0.00264,0.0333],"force_p95":9.15768,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.50039,"mean_force":3.93036,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49962,0.01453,0.02146]},{"body_a":"world","body_b":"push_box","contact_count":1912.0,"contact_point_centroid":[0.50473,-0.02008,-1e-05],"force_p95":1.9069,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.09032,"mean_force":0.41876,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4982,0.03573,0.02529]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.51013,-0.13074,0.0501],"force_p95":0.90426,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.95185,"mean_force":0.47593,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49588,-0.11882,0.01982]},{"body_a":"world","body_b":"push_box","contact_count":3808.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4992,0.02862,0.16611]}],"total_contact_groups":9},"final_pose_error":0.14389,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50062,-0.15613,0.02499],"final_tcp_position":[0.49431,0.02251,0.08352],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":69.80636,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":952.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3808.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.50029,0.05777,0.03327],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07714,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":525.0,"n_steps_budget":600.0,"object_pos_end":[0.5057,-0.02631,0.02501],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.12382,"object_to_goal_dist_start":0.13127,"object_z_max":0.02509,"peak_contact_force":1.58685,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1995.0,"raw_peak_contact_force":13.50039,"tcp_end":[0.5,0.01046,0.02083],"tcp_start":[0.50029,0.05777,0.03327],"tcp_to_object_dist_end":0.03745,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":858.0,"n_steps_budget":1000.0,"object_pos_end":[0.50034,-0.1557,0.02504],"object_pos_start":[0.5057,-0.02631,0.02501],"object_to_goal_dist_end":0.00571,"object_to_goal_dist_start":0.12382,"object_z_max":0.02781,"peak_contact_force":1.65648,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2546.0,"raw_peak_contact_force":69.80636,"tcp_end":[0.4959,-0.11878,0.01983],"tcp_start":[0.5,0.01046,0.02083],"tcp_to_object_dist_end":0.03755,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50062,-0.15613,0.02499],"object_pos_start":[0.50034,-0.1557,0.02504],"object_to_goal_dist_end":0.00616,"object_to_goal_dist_start":0.00571,"object_z_max":0.02777,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3869.0,"raw_peak_contact_force":17.45094,"tcp_end":[0.49431,0.02251,0.08352],"tcp_start":[0.4959,-0.11878,0.01983],"tcp_to_object_dist_end":0.18809,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```