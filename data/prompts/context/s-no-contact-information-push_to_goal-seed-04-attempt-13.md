## Search State

- **Seed**: 4
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.4177 | 0.79 | ❌ rejected |
| 12 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 14 | -0.2265 | 0.66 | ❌ rejected |
| 11 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.6239 | 0.03 | ❌ rejected |
| 10 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.5048 | 0.15 | ❌ rejected |
| 9 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 13 | -0.6273 | 0.07 | ❌ rejected |

**Proposal policy**: task_score is 0.79 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.418) — your mutation base

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

- **Composite score**: 0.418
- **task_score** (E): 0.793
- **fitness_score**: 0.444  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| push_1 | 1.00 | 0.1876 |
| align_1 | 1.00 | 0.1812 |
| release_1 | 0.33 | 0.1678 |
| insert_1 | 1.00 | 0.0012 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| push_1 | push | 1.00 / time_limit | (0.500, -0.000, 0.301)→(0.497, -0.068, 0.126) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 |
| align_1 | align | 1.00 / step_budget | (0.497, -0.068, 0.126)→(0.527, 0.079, 0.027) | (0.531, 0.007, 0.025)→(0.533, 0.017, 0.028) | 0.161→0.171 |
| release_1 | release | 0.33 / step_budget | (0.527, 0.079, 0.027)→(0.505, -0.087, 0.021) | (0.533, 0.017, 0.028)→(0.522, -0.131, 0.025) | 0.171→0.036 |
| insert_1 | insert | 1.00 / force_exceeded | (0.505, -0.087, 0.021)→(0.504, -0.088, 0.020) | (0.522, -0.131, 0.025)→(0.522, -0.131, 0.025) | 0.036→0.036 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- approach_alignment: 0.695
- goal_progress: 0.927
- terminal_score: 0.927
- phase_score: 0.219
- phase_breakdown.approach_score: 0.821
- phase_breakdown.push_score: 0.110

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.502
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.927
- **Median Q (composite search score)**: 0.406
- **K-run variance**: 0.0019
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.328


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.61594,"average_solve_count":138.0,"average_success_count":138.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00022,"align_1.lateral_offset_y":0.00233,"insert_1.insertion_depth":0.08164,"insert_1.insertion_force":12.12963,"push_1.push_distance":0.08817,"push_1.push_speed":0.06182},"optimized_scores":{"best_composite_score":0.40639,"best_fitness_score":0.43305,"best_task_score":0.77322},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":2226.0,"contact_point_centroid":[0.55532,-0.05659,-0.00016],"force_p95":56.66942,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":82.50517,"mean_force":20.01619,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52609,-0.01024,0.02122]},{"body_a":"push_box","body_b":"link7","contact_count":1072.0,"contact_point_centroid":[0.56095,-0.04897,0.04976],"force_p95":57.25637,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":62.9878,"mean_force":34.7162,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52205,-0.03012,0.02143]},{"body_a":"attachment","body_b":"push_box","contact_count":877.0,"contact_point_centroid":[0.5292,-0.0553,0.03794],"force_p95":42.55982,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":52.83756,"mean_force":14.27541,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51919,-0.04475,0.02172]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54613,-0.11133,0.04917],"force_p95":45.06465,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.06465,"mean_force":45.06465,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50895,-0.0924,0.02117]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.53213,-0.13336,-0.00014],"force_p95":26.2772,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.39512,"mean_force":13.8413,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50895,-0.0924,0.02117]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.53063,-0.10062,0.04952],"force_p95":12.62352,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.62352,"mean_force":12.62352,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50895,-0.0924,0.02117]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49725,-0.02673,0.21083]},{"body_a":"world","body_b":"push_box","contact_count":3116.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.52056,0.01232,0.07133]}],"total_contact_groups":8},"final_pose_error":0.05842,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53229,-0.13325,0.02472],"final_tcp_position":[0.50895,-0.0924,0.02117],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"phases":[{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","tcp_end":[0.49651,-0.05338,0.12547],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12768,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":779.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","tcp_end":[0.54607,0.07449,0.02384],"tcp_start":[0.49651,-0.05338,0.12547],"tcp_to_object_dist_end":0.07349,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53229,-0.13324,0.02472],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.03638,"object_to_goal_dist_start":0.16043,"object_z_max":0.02888,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.50895,-0.0924,0.02117],"tcp_start":[0.54607,0.07449,0.02384],"tcp_to_object_dist_end":0.04717,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.53229,-0.13325,0.02472],"object_pos_start":[0.53229,-0.13324,0.02472],"object_to_goal_dist_end":0.03638,"object_to_goal_dist_start":0.03638,"object_z_max":0.02472,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","tcp_end":[0.50895,-0.0924,0.02117],"tcp_start":[0.50895,-0.0924,0.02117],"tcp_to_object_dist_end":0.04718,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90551,"average_solve_count":127.0,"average_success_count":127.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00941,"align_1.lateral_offset_y":0.01,"insert_1.insertion_depth":0.12976,"insert_1.insertion_force":9.81121,"push_1.push_distance":0.18604,"push_1.push_speed":0.09949},"optimized_scores":{"best_composite_score":0.37078,"best_fitness_score":0.39744,"best_task_score":0.67738},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":229.0,"contact_point_centroid":[0.53615,0.07044,0.04614],"force_p95":153.88768,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":184.83332,"mean_force":101.07595,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.52884,0.07775,0.04815]},{"body_a":"attachment","body_b":"push_box","contact_count":933.0,"contact_point_centroid":[0.53349,0.02847,0.03471],"force_p95":156.28122,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":164.58355,"mean_force":116.35089,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52933,0.03866,0.03548]},{"body_a":"world","body_b":"push_box","contact_count":3335.0,"contact_point_centroid":[0.53706,0.04046,-7e-05],"force_p95":58.5402,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":149.42694,"mean_force":7.85088,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51044,-0.00062,0.0861]},{"body_a":"world","body_b":"push_box","contact_count":2520.0,"contact_point_centroid":[0.53747,-0.02517,-0.00041],"force_p95":105.02845,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":114.9744,"mean_force":58.22574,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52589,0.02155,0.03319]},{"body_a":"push_box","body_b":"link7","contact_count":973.0,"contact_point_centroid":[0.56208,0.00564,0.06871],"force_p95":72.63408,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":85.80025,"mean_force":51.31651,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5296,0.04182,0.03535]},{"body_a":"push_box","body_b":"link7","contact_count":33.0,"contact_point_centroid":[0.56737,0.07378,0.06701],"force_p95":75.81257,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":75.87224,"mean_force":62.64961,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.53396,0.10636,0.03421]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.55376,-0.07267,0.04997],"force_p95":18.40215,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.40215,"mean_force":18.40215,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.51038,-0.04978,0.02278]},{"body_a":"world","body_b":"push_box","contact_count":88.0,"contact_point_centroid":[0.53624,-0.10036,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.29103,"mean_force":0.45247,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.51129,-0.04833,0.02363]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49729,-0.04339,0.21544]}],"total_contact_groups":9},"final_pose_error":0.10064,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53624,-0.10037,0.02499],"final_tcp_position":[0.5103,-0.04991,0.02271],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"phases":[{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","tcp_end":[0.49659,-0.08551,0.1368],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.17059,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":959.0,"n_steps_budget":1000.0,"object_pos_end":[0.54245,0.06695,0.03272],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.2212,"object_to_goal_dist_start":0.1905,"object_z_max":0.03487,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","tcp_end":[0.53507,0.11013,0.03197],"tcp_start":[0.49659,-0.08551,0.1368],"tcp_to_object_dist_end":0.04381,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53624,-0.10036,0.02499],"object_pos_start":[0.54245,0.06695,0.03272],"object_to_goal_dist_end":0.06146,"object_to_goal_dist_start":0.2212,"object_z_max":0.03447,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.51206,-0.04726,0.0244],"tcp_start":[0.53507,0.11013,0.03197],"tcp_to_object_dist_end":0.05835,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":22.0,"n_steps_budget":660.0,"object_pos_end":[0.53624,-0.10037,0.02499],"object_pos_start":[0.53624,-0.10036,0.02499],"object_to_goal_dist_end":0.06146,"object_to_goal_dist_start":0.06146,"object_z_max":0.02499,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","tcp_end":[0.5103,-0.04991,0.02271],"tcp_start":[0.51206,-0.04726,0.0244],"tcp_to_object_dist_end":0.05678,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89916,"average_solve_count":119.0,"average_success_count":119.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00313,"align_1.lateral_offset_y":-0.00538,"insert_1.insertion_depth":0.0542,"insert_1.insertion_force":18.33817,"push_1.push_distance":0.07999,"push_1.push_speed":0.08793},"optimized_scores":{"best_composite_score":0.4758,"best_fitness_score":0.50247,"best_task_score":0.9273},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":803.0,"contact_point_centroid":[0.51196,-0.06674,0.04617],"force_p95":41.63593,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.24108,"mean_force":17.43589,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49695,-0.05552,0.0216]},{"body_a":"world","body_b":"push_box","contact_count":2301.0,"contact_point_centroid":[0.50539,-0.09089,-7e-05],"force_p95":29.92344,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":49.14406,"mean_force":9.47306,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49629,-0.03873,0.02105]},{"body_a":"push_box","body_b":"link7","contact_count":748.0,"contact_point_centroid":[0.52334,-0.07378,0.05321],"force_p95":28.97177,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.60241,"mean_force":16.36149,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49671,-0.05233,0.02129]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.5203,-0.14728,0.04941],"force_p95":40.55877,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.55877,"mean_force":40.55877,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.4938,-0.12025,0.01722]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.49612,-0.15883,-0.00011],"force_p95":20.99732,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.92821,"mean_force":10.4214,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.4938,-0.12025,0.01722]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49722,-0.03213,0.20602]},{"body_a":"world","body_b":"push_box","contact_count":2348.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49676,-0.00533,0.0692]}],"total_contact_groups":7},"final_pose_error":0.03137,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49619,-0.15875,0.02478],"final_tcp_position":[0.4938,-0.12025,0.0172],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"phases":[{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","tcp_end":[0.49648,-0.06387,0.1167],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.1025,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":587.0,"n_steps_budget":990.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","tcp_end":[0.49983,0.05259,0.026],"tcp_start":[0.49648,-0.06387,0.1167],"tcp_to_object_dist_end":0.07156,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49619,-0.15875,0.02478],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.00954,"object_to_goal_dist_start":0.13127,"object_z_max":0.02884,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.4938,-0.12025,0.01722],"tcp_start":[0.49983,0.05259,0.026],"tcp_to_object_dist_end":0.03931,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.49619,-0.15875,0.02478],"object_pos_start":[0.49619,-0.15875,0.02478],"object_to_goal_dist_end":0.00954,"object_to_goal_dist_start":0.00954,"object_z_max":0.02478,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","tcp_end":[0.4938,-0.12025,0.0172],"tcp_start":[0.4938,-0.12025,0.01722],"tcp_to_object_dist_end":0.03931,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```