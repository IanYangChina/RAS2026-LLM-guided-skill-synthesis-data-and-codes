## Search State

- **Seed**: 4
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.4196 | 0.80 | ❌ rejected |
| 13 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.4177 | 0.79 | ❌ rejected |
| 12 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 14 | -0.2265 | 0.66 | ❌ rejected |
| 11 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.6239 | 0.03 | ❌ rejected |
| 10 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.5048 | 0.15 | ❌ rejected |

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
- **task_score** (E): 0.798
- **fitness_score**: 0.446  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| push_1 | 1.00 | 0.1891 |
| align_1 | 1.00 | 0.1782 |
| release_1 | 0.33 | 0.1669 |
| insert_1 | 1.00 | 0.0025 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| push_1 | push | 1.00 / time_limit | (0.500, -0.000, 0.301)→(0.496, -0.065, 0.124) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 |
| align_1 | align | 1.00 / step_budget | (0.496, -0.065, 0.124)→(0.527, 0.079, 0.027) | (0.531, 0.007, 0.025)→(0.533, 0.017, 0.028) | 0.161→0.171 |
| release_1 | release | 0.33 / step_budget | (0.527, 0.079, 0.027)→(0.506, -0.086, 0.022) | (0.533, 0.017, 0.028)→(0.522, -0.131, 0.025) | 0.171→0.035 |
| insert_1 | insert | 1.00 / force_exceeded | (0.506, -0.086, 0.022)→(0.505, -0.088, 0.021) | (0.522, -0.131, 0.025)→(0.522, -0.131, 0.025) | 0.035→0.035 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- approach_alignment: 0.696
- goal_progress: 0.938
- terminal_score: 0.938
- phase_score: 0.217
- phase_breakdown.approach_score: 0.821
- phase_breakdown.push_score: 0.106

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.506
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.938
- **Median Q (composite search score)**: 0.406
- **K-run variance**: 0.0019
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.263


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.68657,"average_solve_count":134.0,"average_success_count":134.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00273,"align_1.lateral_offset_y":-0.00141,"insert_1.insertion_depth":0.08787,"insert_1.insertion_force":10.9744,"push_1.push_distance":0.06227,"push_1.push_speed":0.06588},"optimized_scores":{"best_composite_score":0.40636,"best_fitness_score":0.43302,"best_task_score":0.77287},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":2222.0,"contact_point_centroid":[0.55522,-0.05597,-0.00016],"force_p95":56.00845,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":83.95571,"mean_force":20.38459,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52627,-0.009,0.02114]},{"body_a":"push_box","body_b":"link7","contact_count":1075.0,"contact_point_centroid":[0.56078,-0.04856,0.04982],"force_p95":57.94476,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":63.7991,"mean_force":35.26454,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52219,-0.02926,0.02138]},{"body_a":"attachment","body_b":"push_box","contact_count":878.0,"contact_point_centroid":[0.5292,-0.0548,0.03793],"force_p95":45.24013,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":54.44462,"mean_force":14.66376,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51929,-0.04421,0.0217]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54612,-0.11073,0.04921],"force_p95":43.81077,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.81077,"mean_force":43.81077,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50913,-0.09148,0.02113]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.53171,-0.13245,-0.00014],"force_p95":25.51242,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.56502,"mean_force":13.58281,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50913,-0.09148,0.02113]},{"body_a":"attachment","body_b":"push_box","contact_count":9.0,"contact_point_centroid":[0.53385,0.02647,0.04993],"force_p95":19.69525,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.69809,"mean_force":18.28132,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.52849,0.03698,0.05198]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.53067,-0.09983,0.04956],"force_p95":12.93983,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.93983,"mean_force":12.93983,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50913,-0.09148,0.02113]},{"body_a":"world","body_b":"push_box","contact_count":2878.0,"contact_point_centroid":[0.55319,0.00155,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.73998,"mean_force":0.30443,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.52036,0.01883,0.0658]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49721,-0.01998,0.20536]}],"total_contact_groups":9},"final_pose_error":0.05935,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53188,-0.13235,0.02473],"final_tcp_position":[0.50914,-0.09148,0.02112],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"phases":[{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","tcp_end":[0.49641,-0.03997,0.11414],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11348,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":725.0,"n_steps_budget":1000.0,"object_pos_end":[0.55324,0.00137,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16046,"object_to_goal_dist_start":0.16043,"object_z_max":0.02503,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","tcp_end":[0.54588,0.07475,0.02357],"tcp_start":[0.49641,-0.03997,0.11414],"tcp_to_object_dist_end":0.07377,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53188,-0.13235,0.02473],"object_pos_start":[0.55324,0.00137,0.02499],"object_to_goal_dist_end":0.03644,"object_to_goal_dist_start":0.16046,"object_z_max":0.02876,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.50913,-0.09148,0.02113],"tcp_start":[0.54588,0.07475,0.02357],"tcp_to_object_dist_end":0.0469,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.53188,-0.13235,0.02473],"object_pos_start":[0.53188,-0.13235,0.02473],"object_to_goal_dist_end":0.03644,"object_to_goal_dist_start":0.03644,"object_z_max":0.02473,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","tcp_end":[0.50914,-0.09148,0.02112],"tcp_start":[0.50913,-0.09148,0.02113],"tcp_to_object_dist_end":0.04691,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90625,"average_solve_count":128.0,"average_success_count":128.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00069,"align_1.lateral_offset_y":-0.00876,"insert_1.insertion_depth":0.07428,"insert_1.insertion_force":8.0359,"push_1.push_distance":0.18511,"push_1.push_speed":0.09956},"optimized_scores":{"best_composite_score":0.37356,"best_fitness_score":0.40023,"best_task_score":0.68343},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":230.0,"contact_point_centroid":[0.53616,0.07037,0.04616],"force_p95":154.39189,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":185.33001,"mean_force":101.50468,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.52884,0.07767,0.04817]},{"body_a":"attachment","body_b":"push_box","contact_count":942.0,"contact_point_centroid":[0.53346,0.02785,0.0347],"force_p95":156.61265,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":166.31744,"mean_force":116.63664,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5293,0.03804,0.03547]},{"body_a":"world","body_b":"push_box","contact_count":3329.0,"contact_point_centroid":[0.53706,0.04049,-7e-05],"force_p95":59.86454,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":149.74193,"mean_force":7.92562,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51042,-0.00053,0.08592]},{"body_a":"world","body_b":"push_box","contact_count":2479.0,"contact_point_centroid":[0.5375,-0.02428,-0.00043],"force_p95":105.57667,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":118.39136,"mean_force":59.97612,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52648,0.02316,0.03362]},{"body_a":"push_box","body_b":"link7","contact_count":981.0,"contact_point_centroid":[0.56204,0.00518,0.06869],"force_p95":72.66853,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":86.40192,"mean_force":51.72067,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52957,0.04129,0.03534]},{"body_a":"push_box","body_b":"link7","contact_count":33.0,"contact_point_centroid":[0.56739,0.07392,0.06698],"force_p95":75.66659,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":75.72635,"mean_force":62.73754,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.53398,0.10644,0.03418]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.5537,-0.07404,0.04997],"force_p95":17.27083,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.27083,"mean_force":17.27083,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.51036,-0.0512,0.02277]},{"body_a":"world","body_b":"push_box","contact_count":180.0,"contact_point_centroid":[0.53611,-0.10169,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.05794,"mean_force":0.33994,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.51198,-0.04811,0.0242]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49729,-0.04324,0.21522]}],"total_contact_groups":9},"final_pose_error":0.09921,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53611,-0.1017,0.02499],"final_tcp_position":[0.51031,-0.05135,0.02273],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"phases":[{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","tcp_end":[0.49657,-0.0852,0.13639],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.1701,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":958.0,"n_steps_budget":1000.0,"object_pos_end":[0.54246,0.06704,0.03269],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.22129,"object_to_goal_dist_start":0.1905,"object_z_max":0.03486,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","tcp_end":[0.53509,0.11024,0.03192],"tcp_start":[0.49657,-0.0852,0.13639],"tcp_to_object_dist_end":0.04383,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53611,-0.10168,0.02499],"object_pos_start":[0.54246,0.06704,0.03269],"object_to_goal_dist_end":0.06032,"object_to_goal_dist_start":0.22129,"object_z_max":0.03446,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.51368,-0.04556,0.02584],"tcp_start":[0.53509,0.11024,0.03192],"tcp_to_object_dist_end":0.06044,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":45.0,"n_steps_budget":690.0,"object_pos_end":[0.53611,-0.1017,0.02499],"object_pos_start":[0.53611,-0.10168,0.02499],"object_to_goal_dist_end":0.06031,"object_to_goal_dist_start":0.06032,"object_z_max":0.02499,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","tcp_end":[0.51031,-0.05135,0.02273],"tcp_start":[0.51368,-0.04556,0.02584],"tcp_to_object_dist_end":0.05661,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.9,"average_solve_count":120.0,"average_success_count":120.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00639,"align_1.lateral_offset_y":0.00093,"insert_1.insertion_depth":0.08851,"insert_1.insertion_force":16.16255,"push_1.push_distance":0.09178,"push_1.push_speed":0.08486},"optimized_scores":{"best_composite_score":0.47891,"best_fitness_score":0.50557,"best_task_score":0.93825},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":2458.0,"contact_point_centroid":[0.50618,-0.09268,-9e-05],"force_p95":36.13361,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":56.88655,"mean_force":10.43104,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49654,-0.04268,0.02129]},{"body_a":"attachment","body_b":"push_box","contact_count":745.0,"contact_point_centroid":[0.51227,-0.06151,0.0463],"force_p95":46.5592,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":55.12328,"mean_force":20.64018,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49727,-0.05038,0.02201]},{"body_a":"push_box","body_b":"link7","contact_count":705.0,"contact_point_centroid":[0.52453,-0.07394,0.05327],"force_p95":35.09184,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.50459,"mean_force":21.49353,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49708,-0.05246,0.02168]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.52434,-0.14656,0.04924],"force_p95":44.83672,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.83672,"mean_force":44.83672,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49494,-0.1203,0.01826]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.49937,-0.1582,-0.00014],"force_p95":25.32611,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.9445,"mean_force":11.46404,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49494,-0.1203,0.01826]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49724,-0.03487,0.20876]},{"body_a":"world","body_b":"push_box","contact_count":2448.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49679,-0.0079,0.07201]}],"total_contact_groups":7},"final_pose_error":0.03088,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49946,-0.15808,0.02471],"final_tcp_position":[0.49494,-0.1203,0.01825],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"phases":[{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","tcp_end":[0.49648,-0.06921,0.12237],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10995,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":612.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","tcp_end":[0.49986,0.0526,0.0261],"tcp_start":[0.49648,-0.06921,0.12237],"tcp_to_object_dist_end":0.07157,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49946,-0.15808,0.02472],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.0081,"object_to_goal_dist_start":0.13127,"object_z_max":0.02913,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.49494,-0.1203,0.01826],"tcp_start":[0.49986,0.0526,0.0261],"tcp_to_object_dist_end":0.0386,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.49946,-0.15808,0.02471],"object_pos_start":[0.49946,-0.15808,0.02472],"object_to_goal_dist_end":0.00811,"object_to_goal_dist_start":0.0081,"object_z_max":0.02472,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","tcp_end":[0.49494,-0.1203,0.01825],"tcp_start":[0.49494,-0.1203,0.01826],"tcp_to_object_dist_end":0.0386,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```