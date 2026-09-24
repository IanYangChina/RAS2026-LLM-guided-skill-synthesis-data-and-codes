## Search State

- **Seed**: 4
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.4196 | 0.80 | ❌ rejected |
| 5 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.5726 | 0.36 | ❌ rejected |
| 4 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.4288 | 0.84 | ✅ accepted |
| 3 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.4198 | 0.80 | ✅ accepted |
| 2 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | time_limit | 4 | -0.0519 | 0.00 | ❌ rejected |

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
- **task_score** (E): 0.797
- **fitness_score**: 0.446  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| push_1 | 1.00 | 0.1880 |
| align_1 | 1.00 | 0.1829 |
| release_1 | 0.33 | 0.1687 |
| insert_1 | 1.00 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| push_1 | push | 1.00 / time_limit | (0.500, -0.000, 0.301)→(0.496, -0.069, 0.127) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 |
| align_1 | align | 1.00 / step_budget | (0.496, -0.069, 0.127)→(0.527, 0.079, 0.027) | (0.531, 0.007, 0.025)→(0.534, 0.016, 0.028) | 0.161→0.171 |
| release_1 | release | 0.33 / step_budget | (0.527, 0.079, 0.027)→(0.504, -0.087, 0.020) | (0.534, 0.016, 0.028)→(0.521, -0.131, 0.025) | 0.171→0.035 |
| insert_1 | insert | 1.00 / force_exceeded | (0.504, -0.087, 0.020)→(0.504, -0.087, 0.020) | (0.521, -0.131, 0.025)→(0.521, -0.131, 0.025) | 0.035→0.035 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- approach_alignment: 0.695
- goal_progress: 0.930
- terminal_score: 0.930
- phase_score: 0.220
- phase_breakdown.approach_score: 0.821
- phase_breakdown.push_score: 0.111

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.504
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.930
- **Median Q (composite search score)**: 0.412
- **K-run variance**: 0.0020
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.282


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.68382,"average_solve_count":136.0,"average_success_count":136.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00055,"align_1.lateral_offset_y":-0.0001,"insert_1.insertion_depth":0.08722,"insert_1.insertion_force":13.69233,"push_1.push_distance":0.07858,"push_1.push_speed":0.06394},"optimized_scores":{"best_composite_score":0.41156,"best_fitness_score":0.43823,"best_task_score":0.7838},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":27.0,"contact_point_centroid":[0.5361,0.0272,0.0496],"force_p95":68.44498,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":97.72877,"mean_force":35.15031,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.53025,0.03724,0.05171]},{"body_a":"world","body_b":"push_box","contact_count":2217.0,"contact_point_centroid":[0.5552,-0.05616,-0.00016],"force_p95":54.3181,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":84.22039,"mean_force":19.90426,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52605,-0.01013,0.02111]},{"body_a":"push_box","body_b":"link7","contact_count":1075.0,"contact_point_centroid":[0.56075,-0.04941,0.04973],"force_p95":55.60424,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":62.70753,"mean_force":34.43251,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.522,-0.03006,0.02132]},{"body_a":"world","body_b":"push_box","contact_count":2968.0,"contact_point_centroid":[0.55334,0.00186,-2e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":59.95028,"mean_force":0.57014,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.52026,0.01383,0.06899]},{"body_a":"attachment","body_b":"push_box","contact_count":879.0,"contact_point_centroid":[0.52824,-0.05579,0.03689],"force_p95":39.56091,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.27444,"mean_force":13.52575,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51906,-0.04509,0.02161]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54538,-0.11273,0.04914],"force_p95":46.12666,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.12666,"mean_force":46.12666,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50861,-0.09308,0.02097]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.5307,-0.13432,-0.00014],"force_p95":26.82897,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.94342,"mean_force":14.03839,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50861,-0.09308,0.02097]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.53013,-0.10154,0.0495],"force_p95":12.46128,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.46128,"mean_force":12.46128,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50861,-0.09308,0.02097]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49723,-0.02457,0.208]}],"total_contact_groups":9},"final_pose_error":0.05771,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53087,-0.13419,0.02471],"final_tcp_position":[0.50861,-0.09308,0.02096],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"phases":[{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","tcp_end":[0.49643,-0.04909,0.11976],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12143,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":757.0,"n_steps_budget":1000.0,"object_pos_end":[0.55372,0.00134,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16059,"object_to_goal_dist_start":0.16043,"object_z_max":0.02528,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","tcp_end":[0.546,0.07453,0.0237],"tcp_start":[0.49643,-0.04909,0.11976],"tcp_to_object_dist_end":0.07361,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53087,-0.13419,0.02471],"object_pos_start":[0.55372,0.00134,0.02499],"object_to_goal_dist_end":0.03468,"object_to_goal_dist_start":0.16059,"object_z_max":0.02862,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.50861,-0.09308,0.02097],"tcp_start":[0.546,0.07453,0.0237],"tcp_to_object_dist_end":0.04689,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.53087,-0.13419,0.02471],"object_pos_start":[0.53087,-0.13419,0.02471],"object_to_goal_dist_end":0.03468,"object_to_goal_dist_start":0.03468,"object_z_max":0.02471,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","tcp_end":[0.50861,-0.09308,0.02096],"tcp_start":[0.50861,-0.09308,0.02097],"tcp_to_object_dist_end":0.0469,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90551,"average_solve_count":127.0,"average_success_count":127.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00673,"align_1.lateral_offset_y":0.00391,"insert_1.insertion_depth":0.0604,"insert_1.insertion_force":2.89791,"push_1.push_distance":0.1873,"push_1.push_speed":0.09635},"optimized_scores":{"best_composite_score":0.37001,"best_fitness_score":0.39668,"best_task_score":0.67813},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":220.0,"contact_point_centroid":[0.53596,0.07112,0.04597],"force_p95":152.73089,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":180.7845,"mean_force":98.28343,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.52874,0.07852,0.04797]},{"body_a":"attachment","body_b":"push_box","contact_count":917.0,"contact_point_centroid":[0.53349,0.02979,0.03469],"force_p95":153.73548,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":162.5766,"mean_force":115.4048,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52939,0.04002,0.03544]},{"body_a":"world","body_b":"push_box","contact_count":3350.0,"contact_point_centroid":[0.53703,0.0403,-7e-05],"force_p95":56.06584,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":147.16365,"mean_force":7.39538,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.5104,-0.00036,0.08705]},{"body_a":"world","body_b":"push_box","contact_count":2432.0,"contact_point_centroid":[0.5376,-0.02315,-0.00041],"force_p95":102.93933,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":113.87041,"mean_force":58.82972,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52579,0.02348,0.03297]},{"body_a":"push_box","body_b":"link7","contact_count":1044.0,"contact_point_centroid":[0.56135,-0.00033,0.0673],"force_p95":72.8031,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":84.26681,"mean_force":46.41763,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52806,0.03528,0.03433]},{"body_a":"push_box","body_b":"link7","contact_count":34.0,"contact_point_centroid":[0.56732,0.07328,0.06714],"force_p95":77.42292,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":77.55111,"mean_force":64.26203,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.53386,0.10626,0.03431]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.55328,-0.07267,0.04975],"force_p95":31.1278,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.1278,"mean_force":31.1278,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50986,-0.0495,0.02248]},{"body_a":"world","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.54267,-0.09075,-4e-05],"force_p95":20.59583,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.22268,"mean_force":10.76496,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50986,-0.0495,0.02248]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49729,-0.0433,0.21629]}],"total_contact_groups":9},"final_pose_error":0.10101,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53539,-0.09993,0.02494],"final_tcp_position":[0.50986,-0.0495,0.02247],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"phases":[{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","tcp_end":[0.49655,-0.08524,0.13865],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.17162,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":958.0,"n_steps_budget":1000.0,"object_pos_end":[0.5424,0.06683,0.03281],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.22108,"object_to_goal_dist_start":0.1905,"object_z_max":0.0349,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","tcp_end":[0.53507,0.11016,0.03203],"tcp_start":[0.49655,-0.08524,0.13865],"tcp_to_object_dist_end":0.04395,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53538,-0.09993,0.02494],"object_pos_start":[0.5424,0.06683,0.03281],"object_to_goal_dist_end":0.06131,"object_to_goal_dist_start":0.22108,"object_z_max":0.03449,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.50986,-0.0495,0.02248],"tcp_start":[0.53507,0.11016,0.03203],"tcp_to_object_dist_end":0.05657,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":1.0,"n_steps_budget":660.0,"object_pos_end":[0.53539,-0.09993,0.02494],"object_pos_start":[0.53538,-0.09993,0.02494],"object_to_goal_dist_end":0.06132,"object_to_goal_dist_start":0.06131,"object_z_max":0.02494,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","tcp_end":[0.50986,-0.0495,0.02247],"tcp_start":[0.50986,-0.0495,0.02248],"tcp_to_object_dist_end":0.05657,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89565,"average_solve_count":115.0,"average_success_count":115.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00207,"align_1.lateral_offset_y":-0.0054,"insert_1.insertion_depth":0.10228,"insert_1.insertion_force":15.85412,"push_1.push_distance":0.09848,"push_1.push_speed":0.09905},"optimized_scores":{"best_composite_score":0.47733,"best_fitness_score":0.504,"best_task_score":0.93025},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":38.0,"contact_point_centroid":[0.50468,0.00833,0.04925],"force_p95":82.82998,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":108.45856,"mean_force":52.42884,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49864,0.01798,0.05183]},{"body_a":"world","body_b":"push_box","contact_count":2416.0,"contact_point_centroid":[0.50471,-0.01795,-3e-05],"force_p95":0.30568,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":75.06166,"mean_force":1.08112,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49685,-0.01123,0.0727]},{"body_a":"world","body_b":"push_box","contact_count":2298.0,"contact_point_centroid":[0.50643,-0.09217,-8e-05],"force_p95":38.7067,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":57.80797,"mean_force":10.90654,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49643,-0.04034,0.0211]},{"body_a":"attachment","body_b":"push_box","contact_count":787.0,"contact_point_centroid":[0.51309,-0.06422,0.04738],"force_p95":44.08037,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":53.5591,"mean_force":20.49525,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49729,-0.0531,0.02191]},{"body_a":"push_box","body_b":"link7","contact_count":808.0,"contact_point_centroid":[0.52329,-0.07559,0.05349],"force_p95":35.01918,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.25137,"mean_force":18.23283,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49692,-0.05505,0.02143]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.52003,-0.14675,0.04945],"force_p95":39.51616,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.51616,"mean_force":39.51616,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.4938,-0.11964,0.01716]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.49589,-0.15828,-0.0001],"force_p95":20.24681,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.115,"mean_force":10.16156,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.4938,-0.11964,0.01716]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49724,-0.03716,0.20832]}],"total_contact_groups":8},"final_pose_error":0.03197,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49595,-0.15821,0.0248],"final_tcp_position":[0.4938,-0.11964,0.01715],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"phases":[{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","tcp_end":[0.49644,-0.07358,0.12193],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11165,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":626.0,"n_steps_budget":1000.0,"object_pos_end":[0.50508,-0.019,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.1311,"object_to_goal_dist_start":0.13127,"object_z_max":0.02638,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","tcp_end":[0.49992,0.05256,0.02599],"tcp_start":[0.49644,-0.07358,0.12193],"tcp_to_object_dist_end":0.07175,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49595,-0.15821,0.0248],"object_pos_start":[0.50508,-0.019,0.02499],"object_to_goal_dist_end":0.00915,"object_to_goal_dist_start":0.1311,"object_z_max":0.02894,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.4938,-0.11964,0.01716],"tcp_start":[0.49992,0.05256,0.02599],"tcp_to_object_dist_end":0.03938,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.49595,-0.15821,0.0248],"object_pos_start":[0.49595,-0.15821,0.0248],"object_to_goal_dist_end":0.00916,"object_to_goal_dist_start":0.00915,"object_z_max":0.0248,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","tcp_end":[0.4938,-0.11964,0.01715],"tcp_start":[0.4938,-0.11964,0.01716],"tcp_to_object_dist_end":0.03938,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```