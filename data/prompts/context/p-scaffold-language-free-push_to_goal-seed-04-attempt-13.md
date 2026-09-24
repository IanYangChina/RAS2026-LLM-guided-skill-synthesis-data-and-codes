## Search State

- **Seed**: 4
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.3298 | 0.73 | ❌ rejected |
| 12 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.1826 | 0.00 | ❌ rejected |
| 11 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | -0.0152 | 0.01 | ❌ rejected |
| 10 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.3516 | 0.76 | ❌ rejected |
| 9 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.3486 | 0.76 | ✅ accepted |

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

## Current Skill (Q=0.330) — your mutation base

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

- **Composite score**: 0.330
- **task_score** (E): 0.731
- **fitness_score**: 0.690  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2781 |
| contact_1 | 1.00 | 1.00 | 0.0480 |
| push_1 | 1.00 | 0.67 | 0.1249 |
| retract_1 | 0.00 | 1.00 | 0.1376 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.525, 0.080, 0.037) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.525, 0.080, 0.037)→(0.527, 0.035, 0.021) | (0.531, 0.007, 0.025)→(0.533, -0.001, 0.025) | 0.161→0.153 | 1.00 / 2.333 | 1.213 | 14.608 |
| push_1 | push | 1.00 / step_budget | (0.527, 0.035, 0.021)→(0.504, -0.086, 0.026) | (0.533, -0.001, 0.025)→(0.524, -0.117, 0.029) | 0.153→0.045 | 0.67 / 2.667 | 76.882 | 102.919 |
| retract_1 | retract | 0.00 / step_budget | (0.504, -0.086, 0.026)→(0.498, 0.037, 0.086) | (0.524, -0.117, 0.029)→(0.521, -0.111, 0.025) | 0.045→0.047 | 1.00 / 4.000 | 0.245 | 62.186 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.465
- goal_progress: 0.969
- terminal_score: 0.969
- phase_score: 0.831
- phase_breakdown.push_score: 0.817
- phase_breakdown.approach_score: 0.821
- phase_breakdown.contact_score: 0.860

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.886
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.969
- **Median Q (composite search score)**: 0.276
- **K-run variance**: 0.0205
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.488


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.31944,"average_solve_count":216.0,"average_success_count":216.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.02529,"contact_1.contact_force":11.9353,"push_1.push_depth":0.09959,"push_1.push_distance":0.13739,"push_1.push_speed":0.08068,"retract_1.speed":0.07549},"optimized_scores":{"best_composite_score":0.27602,"best_fitness_score":0.63602,"best_task_score":0.63153},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":967.0,"contact_point_centroid":[0.56257,-0.04705,0.05404],"force_p95":123.87987,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":136.4382,"mean_force":80.20203,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5264,-0.03246,0.02442]},{"body_a":"world","body_b":"push_box","contact_count":1916.0,"contact_point_centroid":[0.55697,-0.07962,-0.00038],"force_p95":85.13552,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":97.52438,"mean_force":51.12732,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52636,-0.03275,0.0245]},{"body_a":"world","body_b":"push_box","contact_count":3621.0,"contact_point_centroid":[0.53602,-0.10274,-3e-05],"force_p95":0.46373,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":82.8586,"mean_force":0.59878,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50263,-0.01656,0.06238]},{"body_a":"attachment","body_b":"push_box","contact_count":968.0,"contact_point_centroid":[0.5461,-0.04068,0.05511],"force_p95":79.52351,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":82.36771,"mean_force":49.3059,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52645,-0.03234,0.02443]},{"body_a":"push_box","body_b":"link7","contact_count":58.0,"contact_point_centroid":[0.55051,-0.09484,0.05706],"force_p95":62.73482,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":78.6265,"mean_force":28.19123,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50824,-0.0872,0.0311]},{"body_a":"attachment","body_b":"push_box","contact_count":74.0,"contact_point_centroid":[0.53256,-0.08865,0.06174],"force_p95":42.16154,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":62.21937,"mean_force":15.44146,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50758,-0.08437,0.03177]},{"body_a":"attachment","body_b":"push_box","contact_count":93.0,"contact_point_centroid":[0.5536,0.02269,0.04038],"force_p95":12.47403,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.78547,"mean_force":5.30849,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54728,0.03461,0.02225]},{"body_a":"world","body_b":"push_box","contact_count":1885.0,"contact_point_centroid":[0.55331,-4e-05,-1e-05],"force_p95":2.58968,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.17879,"mean_force":0.51241,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54425,0.05345,0.02941]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52126,0.03684,0.16994]}],"total_contact_groups":9},"final_pose_error":0.12336,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53539,-0.10265,0.02499],"final_tcp_position":[0.50049,0.0415,0.09131],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":136.4382,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.54466,0.07412,0.04176],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07515,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":520.0,"n_steps_budget":600.0,"object_pos_end":[0.55562,-0.00664,0.02487],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.15377,"object_to_goal_dist_start":0.16043,"object_z_max":0.02511,"peak_contact_force":0.6027,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1978.0,"raw_peak_contact_force":16.78547,"tcp_end":[0.54808,0.03036,0.02074],"tcp_start":[0.54466,0.07412,0.04176],"tcp_to_object_dist_end":0.03799,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":984.0,"n_steps_budget":1000.0,"object_pos_end":[0.54189,-0.11518,0.03116],"object_pos_start":[0.55562,-0.00664,0.02487],"object_to_goal_dist_end":0.05482,"object_to_goal_dist_start":0.15377,"object_z_max":0.03116,"peak_contact_force":123.5961,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3851.0,"raw_peak_contact_force":136.4382,"tcp_end":[0.50942,-0.09167,0.02997],"tcp_start":[0.54808,0.03036,0.02074],"tcp_to_object_dist_end":0.0401,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53539,-0.10265,0.02499],"object_pos_start":[0.54189,-0.11518,0.03116],"object_to_goal_dist_end":0.05911,"object_to_goal_dist_start":0.05482,"object_z_max":0.03445,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3753.0,"raw_peak_contact_force":82.8586,"tcp_end":[0.50049,0.0415,0.09131],"tcp_start":[0.50942,-0.09167,0.02997],"tcp_to_object_dist_end":0.16247,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.51707,"average_solve_count":205.0,"average_success_count":205.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.07296,"contact_1.contact_force":2.98199,"push_1.push_depth":0.09289,"push_1.push_distance":0.15432,"push_1.push_speed":0.07653,"retract_1.speed":0.02878},"optimized_scores":{"best_composite_score":0.1875,"best_fitness_score":0.5475,"best_task_score":0.59369},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":929.0,"contact_point_centroid":[0.5482,-0.01139,0.05464],"force_p95":104.8803,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":114.42428,"mean_force":69.97553,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51693,0.00521,0.0235]},{"body_a":"attachment","body_b":"push_box","contact_count":937.0,"contact_point_centroid":[0.53631,-0.00344,0.05349],"force_p95":91.1417,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":96.88022,"mean_force":50.20506,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51705,0.00573,0.02347]},{"body_a":"world","body_b":"push_box","contact_count":3655.0,"contact_point_centroid":[0.52581,-0.07712,-3e-05],"force_p95":0.32312,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":87.40585,"mean_force":0.54566,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50064,0.00868,0.05932]},{"body_a":"push_box","body_b":"link7","contact_count":54.0,"contact_point_centroid":[0.54595,-0.05982,0.05578],"force_p95":79.69192,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":84.54544,"mean_force":38.61518,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50543,-0.04669,0.02947]},{"body_a":"world","body_b":"push_box","contact_count":1793.0,"contact_point_centroid":[0.54191,-0.04709,-0.00032],"force_p95":68.67616,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":78.72271,"mean_force":46.74839,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5167,0.00379,0.02368]},{"body_a":"attachment","body_b":"push_box","contact_count":74.0,"contact_point_centroid":[0.5279,-0.05106,0.05953],"force_p95":61.60188,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":77.37257,"mean_force":22.47361,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50472,-0.0441,0.03024]},{"body_a":"attachment","body_b":"push_box","contact_count":98.0,"contact_point_centroid":[0.53882,0.05792,0.04139],"force_p95":11.43443,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.94644,"mean_force":3.38663,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53109,0.06986,0.0215]},{"body_a":"world","body_b":"push_box","contact_count":1824.0,"contact_point_centroid":[0.53681,0.03512,-1e-05],"force_p95":1.68952,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.28084,"mean_force":0.4363,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52891,0.08895,0.02653]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51416,0.05438,0.1667]}],"total_contact_groups":9},"final_pose_error":0.11481,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52526,-0.07684,0.02499],"final_tcp_position":[0.49932,0.05405,0.08695],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":114.42428,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.53028,0.109,0.0362],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07319,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":519.0,"n_steps_budget":600.0,"object_pos_end":[0.53797,0.02848,0.02504],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.18248,"object_to_goal_dist_start":0.1905,"object_z_max":0.02513,"peak_contact_force":2.29047,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1922.0,"raw_peak_contact_force":12.94644,"tcp_end":[0.5317,0.06543,0.02045],"tcp_start":[0.53028,0.109,0.0362],"tcp_to_object_dist_end":0.03776,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":943.0,"n_steps_budget":1000.0,"object_pos_end":[0.52963,-0.08145,0.03102],"object_pos_start":[0.53797,0.02848,0.02504],"object_to_goal_dist_end":0.07492,"object_to_goal_dist_start":0.18248,"object_z_max":0.03102,"peak_contact_force":107.04881,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3659.0,"raw_peak_contact_force":114.42428,"tcp_end":[0.50641,-0.05006,0.02834],"tcp_start":[0.5317,0.06543,0.02045],"tcp_to_object_dist_end":0.03914,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52526,-0.07684,0.02499],"object_pos_start":[0.52963,-0.08145,0.03102],"object_to_goal_dist_end":0.0774,"object_to_goal_dist_start":0.07492,"object_z_max":0.03348,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3783.0,"raw_peak_contact_force":87.40585,"tcp_end":[0.49932,0.05405,0.08695],"tcp_start":[0.50641,-0.05006,0.02834],"tcp_to_object_dist_end":0.14712,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.63784,"average_solve_count":185.0,"average_success_count":185.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.0783,"contact_1.contact_force":14.67868,"push_1.push_depth":0.09858,"push_1.push_distance":0.0388,"push_1.push_speed":0.06104,"retract_1.speed":0.07193},"optimized_scores":{"best_composite_score":0.52593,"best_fitness_score":0.88593,"best_task_score":0.96904},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1406.0,"contact_point_centroid":[0.506,-0.10466,-0.00011],"force_p95":47.71871,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":57.8949,"mean_force":16.99392,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49754,-0.05136,0.01959]},{"body_a":"push_box","body_b":"link7","contact_count":529.0,"contact_point_centroid":[0.52458,-0.04638,0.05225],"force_p95":39.59304,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.06153,"mean_force":29.24305,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49853,-0.02509,0.0198]},{"body_a":"attachment","body_b":"push_box","contact_count":874.0,"contact_point_centroid":[0.51056,-0.06198,0.04281],"force_p95":36.61594,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.05897,"mean_force":17.64362,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49756,-0.05047,0.01958]},{"body_a":"push_box","body_b":"link7","contact_count":49.0,"contact_point_centroid":[0.52486,-0.13687,0.05037],"force_p95":9.06755,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.29384,"mean_force":5.11891,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49384,-0.1112,0.02048]},{"body_a":"world","body_b":"push_box","contact_count":3824.0,"contact_point_centroid":[0.5011,-0.15322,-2e-05],"force_p95":0.29734,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.52214,"mean_force":0.32321,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4931,-0.04584,0.04984]},{"body_a":"attachment","body_b":"push_box","contact_count":86.0,"contact_point_centroid":[0.50637,0.00252,0.03507],"force_p95":11.18686,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.09083,"mean_force":3.88306,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49963,0.01438,0.02143]},{"body_a":"world","body_b":"push_box","contact_count":1920.0,"contact_point_centroid":[0.5047,-0.01993,-1e-05],"force_p95":1.18295,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.40372,"mean_force":0.4223,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4982,0.03567,0.02525]},{"body_a":"world","body_b":"push_box","contact_count":3576.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49924,0.02863,0.16611]}],"total_contact_groups":8},"final_pose_error":0.15145,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50123,-0.15387,0.02499],"final_tcp_position":[0.49416,0.01586,0.07992],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":57.8949,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":894.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3576.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.5003,0.05778,0.03322],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07715,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":525.0,"n_steps_budget":600.0,"object_pos_end":[0.50659,-0.02615,0.02514],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.12402,"object_to_goal_dist_start":0.13127,"object_z_max":0.02516,"peak_contact_force":0.74478,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2006.0,"raw_peak_contact_force":14.09083,"tcp_end":[0.50002,0.0105,0.02085],"tcp_start":[0.5003,0.05778,0.03322],"tcp_to_object_dist_end":0.03748,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":928.0,"n_steps_budget":1000.0,"object_pos_end":[0.49989,-0.15435,0.02513],"object_pos_start":[0.50659,-0.02615,0.02514],"object_to_goal_dist_end":0.00435,"object_to_goal_dist_start":0.12402,"object_z_max":0.02753,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2809.0,"raw_peak_contact_force":57.8949,"tcp_end":[0.49587,-0.11732,0.01982],"tcp_start":[0.50002,0.0105,0.02085],"tcp_to_object_dist_end":0.03762,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50123,-0.15387,0.02499],"object_pos_start":[0.49989,-0.15435,0.02513],"object_to_goal_dist_end":0.00406,"object_to_goal_dist_start":0.00435,"object_z_max":0.02817,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3873.0,"raw_peak_contact_force":16.29384,"tcp_end":[0.49416,0.01586,0.07992],"tcp_start":[0.49587,-0.11732,0.01982],"tcp_to_object_dist_end":0.17854,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```