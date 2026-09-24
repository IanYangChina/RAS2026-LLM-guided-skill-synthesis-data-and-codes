## Search State

- **Seed**: 4
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 13 | -0.6273 | 0.07 | ❌ rejected |
| 8 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.4172 | 0.79 | ❌ rejected |
| 7 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.4264 | 0.83 | ❌ rejected |
| 6 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.4196 | 0.80 | ❌ rejected |
| 5 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.5726 | 0.36 | ❌ rejected |

**Proposal policy**: task_score is 0.07 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.839, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=-0.627) — your mutation base

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

- **Composite score**: -0.627
- **task_score** (E): 0.071
- **fitness_score**: 0.083  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.710

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_1 | 1.00 | 0.1463 |
| descent_1 | 1.00 | 0.1552 |
| push_1 | 0.00 | 0.0012 |
| retract_1 | 1.00 | 0.1134 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.537, 0.085, 0.194) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 |
| descent_1 | descend | 1.00 / step_budget | (0.537, 0.085, 0.194)→(0.538, 0.063, 0.043) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 |
| push_1 | push | 0.00 / step_budget | (0.542, 0.054, 0.042)→(0.543, 0.053, 0.042) | (0.531, 0.007, 0.025)→(0.531, 0.006, 0.025) | 0.161→0.161 |
| retract_1 | retract | 1.00 / step_budget | (0.543, 0.053, 0.042)→(0.540, 0.053, 0.155) | (0.532, 0.006, 0.025)→(0.526, -0.004, 0.025) | 0.160→0.149 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.216
- approach_alignment: 0.368
- goal_progress: 0.214
- terminal_score: 0.214
- phase_score: 0.087
- phase_breakdown.approach_sub_score: 0.287
- phase_breakdown.push_sub_score: 0.001

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.138
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.214
- **Median Q (composite search score)**: -0.651
- **K-run variance**: 0.0015
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Parameters at lower bound**: push_1.guard_force_threshold
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":7.0,"average_failure_rate":0.04965,"average_mean_iterations":13.97163,"average_solve_count":141.0,"average_success_count":134.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_behind":0.06169,"approach_1.approach_speed":0.08019,"approach_1.approach_z":0.19888,"descent_1.descent_behind":0.06304,"descent_1.descent_speed":0.12794,"push_1.guard_force_threshold":24.50329,"push_1.push_speed":0.02839,"push_1.push_x_offset":-0.00384,"push_1.push_y_offset":0.01495,"push_1.retry_offset_x":0.00932,"push_1.retry_offset_y":-0.00232,"retract_1.retract_speed":0.03657,"retract_1.retract_z":0.09703},"optimized_scores":{"best_composite_score":-0.57217,"best_fitness_score":0.13783,"best_task_score":0.21436},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.57837,0.02406,0.04109],"force_p95":202.89479,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":224.87479,"mean_force":78.2907,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.57997,0.03424,0.03952]},{"body_a":"world","body_b":"push_box","contact_count":60.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":1.23562,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":189.00869,"mean_force":4.03963,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.57189,0.05082,0.0404]},{"body_a":"attachment","body_b":"push_box","contact_count":8.0,"contact_point_centroid":[0.58009,0.01534,0.0444],"force_p95":34.54741,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.33133,"mean_force":10.45059,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.58809,0.02107,0.04111]},{"body_a":"world","body_b":"push_box","contact_count":1058.0,"contact_point_centroid":[0.53733,-0.0294,-6e-05],"force_p95":0.41709,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.71105,"mean_force":0.36571,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5807,0.02639,0.08177]},{"body_a":"world","body_b":"push_box","contact_count":932.0,"contact_point_centroid":[0.55317,0.00136,-0.0],"force_p95":0.24532,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52806,0.02364,0.26595]},{"body_a":"world","body_b":"push_box","contact_count":1380.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descent_1","phase_type":"descend","tcp_position_centroid":[0.56289,0.05382,0.13824]}],"total_contact_groups":6},"final_pose_error":0.01976,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53778,-0.02976,0.02499],"final_tcp_position":[0.58015,0.02807,0.11777],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"phases":[{"n_steps":233.0,"n_steps_budget":960.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_sub","tcp_end":[0.55886,0.04899,0.23156],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.21206,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":345.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"phase_name":"descent_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"approach_sub","tcp_end":[0.56853,0.05895,0.04376],"tcp_start":[0.55886,0.04899,0.23156],"tcp_to_object_dist_end":0.06249,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":17.0,"n_steps_budget":1000.0,"object_pos_end":[0.55326,0.00112,0.02531],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16024,"object_to_goal_dist_start":0.16043,"object_z_max":0.02555,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_sub","tcp_end":[0.58369,0.02844,0.04017],"tcp_start":[0.58168,0.03149,0.03986],"tcp_to_object_dist_end":0.0435,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":308.0,"n_steps_budget":1000.0,"object_pos_end":[0.53778,-0.02976,0.02499],"object_pos_start":[0.55364,9e-05,0.02574],"object_to_goal_dist_end":0.12604,"object_to_goal_dist_start":0.15939,"object_z_max":0.02941,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.58015,0.02807,0.11777],"tcp_start":[0.58369,0.02844,0.04017],"tcp_to_object_dist_end":0.11725,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":38.0,"average_failure_rate":0.2695,"average_mean_iterations":56.75887,"average_solve_count":141.0,"average_success_count":103.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_behind":0.09377,"approach_1.approach_speed":0.13106,"approach_1.approach_z":0.16681,"descent_1.descent_behind":0.05017,"descent_1.descent_speed":0.08701,"push_1.guard_force_threshold":5.00033,"push_1.push_speed":0.13571,"push_1.push_x_offset":-0.00828,"push_1.push_y_offset":-0.00409,"push_1.retry_offset_x":0.00042,"push_1.retry_offset_y":0.00242,"retract_1.retract_speed":0.09405,"retract_1.retract_z":0.14458},"optimized_scores":{"best_composite_score":-0.65142,"best_fitness_score":0.05858,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1352.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52187,0.05523,0.24937]},{"body_a":"world","body_b":"push_box","contact_count":1180.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descent_1","phase_type":"descend","tcp_position_centroid":[0.54335,0.10151,0.1228]},{"body_a":"world","body_b":"push_box","contact_count":1708.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.53904,0.08868,0.103]}],"total_contact_groups":3},"final_pose_error":0.01976,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5366,0.03695,0.02499],"final_tcp_position":[0.5396,0.08879,0.16932],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"phases":[{"n_steps":338.0,"n_steps_budget":870.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_sub","tcp_end":[0.54566,0.11276,0.19933],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.19033,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":295.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.02499,"phase_name":"descent_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"approach_sub","tcp_end":[0.54255,0.08933,0.04427],"tcp_start":[0.54566,0.11276,0.19933],"tcp_to_object_dist_end":0.05613,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":0.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_sub","tcp_end":[0.54255,0.08933,0.04427],"tcp_start":[0.54255,0.08933,0.04427],"tcp_to_object_dist_end":0.05613,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":427.0,"n_steps_budget":960.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.02499,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.5396,0.08879,0.16932],"tcp_start":[0.54255,0.08933,0.04427],"tcp_to_object_dist_end":0.15339,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":41.0,"average_failure_rate":0.27333,"average_mean_iterations":57.18,"average_solve_count":150.0,"average_success_count":109.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_behind":0.12496,"approach_1.approach_speed":0.13345,"approach_1.approach_z":0.11066,"descent_1.descent_behind":0.05008,"descent_1.descent_speed":0.05688,"push_1.guard_force_threshold":9.45153,"push_1.push_speed":0.09486,"push_1.push_x_offset":0.00182,"push_1.push_y_offset":0.00695,"push_1.retry_offset_x":0.0021,"push_1.retry_offset_y":-0.00099,"retract_1.retract_speed":0.12537,"retract_1.retract_z":0.15685},"optimized_scores":{"best_composite_score":-0.6583,"best_fitness_score":0.0517,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1396.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50208,0.04542,0.22545]},{"body_a":"world","body_b":"push_box","contact_count":1000.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descent_1","phase_type":"descend","tcp_position_centroid":[0.50316,0.06847,0.09637]},{"body_a":"world","body_b":"push_box","contact_count":1672.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49961,0.04097,0.10721]}],"total_contact_groups":3},"final_pose_error":0.01972,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50458,-0.01881,0.02499],"final_tcp_position":[0.50013,0.0411,0.17865],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"phases":[{"n_steps":349.0,"n_steps_budget":930.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_sub","tcp_end":[0.50528,0.09316,0.14998],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.16781,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":250.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"phase_name":"descent_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"approach_sub","tcp_end":[0.50274,0.04136,0.04134],"tcp_start":[0.50528,0.09316,0.14998],"tcp_to_object_dist_end":0.06237,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":0.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_sub","tcp_end":[0.50274,0.04136,0.04134],"tcp_start":[0.50274,0.04136,0.04134],"tcp_to_object_dist_end":0.06237,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":418.0,"n_steps_budget":810.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.50013,0.0411,0.17865],"tcp_start":[0.50274,0.04136,0.04134],"tcp_to_object_dist_end":0.16498,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```