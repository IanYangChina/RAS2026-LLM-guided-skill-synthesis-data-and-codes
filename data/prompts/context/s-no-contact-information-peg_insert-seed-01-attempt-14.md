## Search State

- **Seed**: 1
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | time_limit | time_limit | time_limit | 5 | 0.5328 | 0.84 | ❌ rejected |
| 13 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.7475 | 0.96 | ❌ rejected |
| 12 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.7475 | 0.96 | ❌ rejected |
| 11 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.7475 | 0.96 | ❌ rejected |
| 10 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.7475 | 0.96 | ❌ rejected |

**Proposal policy**: task_score is 0.84 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: peg_insert
- Frozen realised-scene SHA-256: `ad40e378f39a19b149b009dee38b90e3211daf0cadc26f2bf0cba9c113417c3b`
- Frozen object start: [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]
- Frozen task target: [0.5009457299760202, 0.03603709570607482, 0.08]
- Frozen socket pose: [0.5009457299760202, 0.03603709570607482, 0.025] (static fixture for this episode)
- Goal object position: (0.5009457299760202, 0.03603709570607482, 0.025)
- Object initial pose: (0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 40.0 N
- Channel axis: `(0.0, 0.0, -1.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth ratio (axial progress into hole)**

## Scene Entities

robot:
  model: panda_peg
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: peg_socket
    role: fixture
    dynamics: static
    geometry: box_with_hole
    base_dimensions_m: [0.12, 0.12, 0.05]
    hole_entry_height_m: 0.08
  - name: peg
    role: manipulated_object
    dynamics: free
    geometry: cylinder
    note: peg is a fixed end-effector attachment on the panda_peg arm
task_landmarks:
  frozen_object_start: [0.504, -0, 0.3403]
  frozen_task_target: [0.5009, 0.036, 0.08]
  frozen_socket_position: [0.5009, 0.036, 0.025]
  socket_state: static_frozen
  frozen_object_starts: {'peg': [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]}
  frozen_targets: {'socket_entry': [0.5009457299760202, 0.03603709570607482, 0.08]}
  frozen_fixtures: {'peg_socket': [0.5009457299760202, 0.03603709570607482, 0.025]}
  insertion_axis: [0, 0, -1]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  hole_depth_m: 0.05
  force_scale_n: 5
  realized_scene_sha256: ad40e378f39a19b149b009dee38b90e3211daf0cadc26f2bf0cba9c113417c3b

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.957, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5009457299760202, 0.03603709570607482, 0.025) | final destination targets |
| `fixture` | offset from fixture pose (0.5009457299760202, 0.03603709570607482, 0.025) | approach/contact targets near fixture |

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

## Current Skill (Q=0.533) — your mutation base

```yaml
skill: peg_insert
phases:
- id: rotate_1
  type: rotate
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
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
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
- id: align_2
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

```

## Design Metrics

- **Composite score**: 0.533
- **task_score** (E): 0.843
- **fitness_score**: 0.843  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| rotate_1 | 1.00 | 0.0017 |
| align_1 | 0.00 | 0.0001 |
| push_1 | 1.00 | 0.1500 |
| align_2 | 1.00 | 0.0708 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| rotate_1 | rotate | 1.00 / time_limit | (0.500, -0.000, 0.301)→(0.499, -0.000, 0.299) | (0.504, -0.000, 0.340)→(0.503, -0.000, 0.339) | 0.260→0.259 |
| align_1 | align | 0.00 / guard_failure | (0.499, -0.000, 0.299)→(0.499, -0.000, 0.299) | (0.503, -0.000, 0.339)→(0.504, -0.000, 0.339) | 0.259→0.259 |
| push_1 | push | 1.00 / time_limit | (0.499, -0.000, 0.299)→(0.472, -0.001, 0.152) | (0.504, -0.000, 0.339)→(0.507, -0.001, 0.135) | 0.259→0.056 |
| align_2 | align | 1.00 / time_limit | (0.472, -0.001, 0.152)→(0.513, 0.004, 0.196) | (0.507, -0.001, 0.135)→(0.540, -0.002, 0.169) | 0.056→0.102 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.848
- alignment_error: None

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.848
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.848
- **Median Q (composite search score)**: 0.536
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.396


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `45273c8d1228632fd57317b0a02550505db6d7cbf023a115124b89e828802a94`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `70dcb1d9cf130ce66aaa294bb82afc0ceb52288177fb1bbf0b6209922022fad5`; realized-scene SHA-256: `ad40e378f39a19b149b009dee38b90e3211daf0cadc26f2bf0cba9c113417c3b`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.50095,0.03604,0.025]},{"name":"target","value":[0.50095,0.03604,0.025]},{"name":"socket","value":[0.50095,0.03604,0.025]},{"name":"goal","value":[0.50095,0.03604,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.50095,0.03604,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.50095,0.03604,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.2561,"average_solve_count":82.0,"average_success_count":82.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00236,"align_1.lateral_offset_y":0.00585,"align_2.lateral_offset_x":-0.00203,"align_2.lateral_offset_y":-0.00449,"push_1.push_distance":0.19238},"optimized_scores":{"best_composite_score":0.53772,"best_fitness_score":0.84772,"best_task_score":0.84772},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link6","contact_count":535.0,"contact_point_centroid":[0.56077,0.01136,0.07936],"force_p95":539.35561,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3030.61033,"mean_force":353.87378,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.47448,0.01892,0.19668]},{"body_a":"world","body_b":"link6","contact_count":41.0,"contact_point_centroid":[0.65225,0.00094,-0.00056],"force_p95":2479.28827,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2596.28038,"mean_force":612.40533,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.51975,0.05707,0.21489]},{"body_a":"peg_socket","body_b":"link6","contact_count":362.0,"contact_point_centroid":[0.56071,0.00512,0.07927],"force_p95":786.3015,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1149.79306,"mean_force":449.91346,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46591,0.00678,0.18592]},{"body_a":"attachment","body_b":"peg_socket","contact_count":12.0,"contact_point_centroid":[0.45682,0.00083,0.07842],"force_p95":1020.33365,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1066.83862,"mean_force":245.94622,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.45222,0.00079,0.0911]},{"body_a":"peg_socket","body_b":"link7","contact_count":844.0,"contact_point_centroid":[0.55993,0.00773,0.07985],"force_p95":488.80339,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1035.01376,"mean_force":292.2943,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4588,0.00396,0.16961]},{"body_a":"peg_socket","body_b":"link7","contact_count":292.0,"contact_point_centroid":[0.56036,0.02391,0.07994],"force_p95":491.59445,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":886.11487,"mean_force":242.59143,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.47445,0.02596,0.18667]}],"total_contact_groups":6},"final_pose_error":0.17991,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50095,0.03604,0.025],"final_tcp_position":[0.55695,0.01121,0.24907],"realised_fixture_position":[0.50095,0.03604,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50095,0.03604,0.08]},"phases":[{"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.50343,-0.0,0.33877],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.25879,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","subtask_id":"approach_socket","tcp_end":[0.49918,-1e-05,0.299],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50356,-0.0,0.33872],"object_pos_start":[0.50343,-0.0,0.33877],"object_to_goal_dist_end":0.25875,"object_to_goal_dist_start":0.25879,"object_z_max":0.33877,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","subtask_id":"approach_socket","tcp_end":[0.49928,-1e-05,0.29895],"tcp_start":[0.49918,-1e-05,0.299],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51152,0.01047,0.17175],"object_pos_start":[0.50356,-0.0,0.33872],"object_to_goal_dist_end":0.09306,"object_to_goal_dist_start":0.25875,"object_z_max":0.3415,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"insert_peg","tcp_end":[0.47968,0.01074,0.19596],"tcp_start":[0.49928,-1e-05,0.29895],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":721.0,"n_steps_budget":750.0,"object_pos_end":[0.5756,0.00541,0.21417],"object_pos_start":[0.51152,0.01047,0.17175],"object_to_goal_dist_end":0.1541,"object_to_goal_dist_start":0.09306,"object_z_max":0.21406,"phase_name":"align_2","phase_peak_obstacle_force":0.0,"phase_type":"align","subtask_id":"insert_peg","tcp_end":[0.55695,0.01121,0.24907],"tcp_start":[0.47968,0.01074,0.19596],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `a0b26c055417598cbe086e53f7823e257fb75222f78e6d5a64925f365f02417e`; realized-scene SHA-256: `418fe4cae2076fb8f01886686f3853ea2b6261693c924940ce72258151551e93`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.48093,-0.01612,0.025]},{"name":"target","value":[0.48093,-0.01612,0.025]},{"name":"socket","value":[0.48093,-0.01612,0.025]},{"name":"goal","value":[0.48093,-0.01612,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,-0.01612,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.48093,-0.01612,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.28571,"average_solve_count":77.0,"average_success_count":77.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00038,"align_1.lateral_offset_y":0.00164,"align_2.lateral_offset_x":-0.00283,"align_2.lateral_offset_y":-0.00057,"push_1.push_distance":0.16069},"optimized_scores":{"best_composite_score":0.53563,"best_fitness_score":0.84563,"best_task_score":0.84563},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":910.0,"contact_point_centroid":[0.54073,-0.00622,0.07984],"force_p95":328.46571,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1453.42461,"mean_force":309.73134,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4682,-0.00265,0.12893]},{"body_a":"attachment","body_b":"peg_socket","contact_count":20.0,"contact_point_centroid":[0.44827,0.00925,0.07937],"force_p95":807.24748,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":883.20219,"mean_force":367.73319,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.44366,-0.00135,0.08801]},{"body_a":"world","body_b":"link6","contact_count":25.0,"contact_point_centroid":[0.68179,-0.03983,-0.00018],"force_p95":861.51737,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":863.06825,"mean_force":445.40645,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49187,0.03679,0.14467]},{"body_a":"peg_socket","body_b":"link7","contact_count":513.0,"contact_point_centroid":[0.54076,-0.00542,0.07995],"force_p95":441.73758,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":643.97661,"mean_force":350.41439,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.47717,0.01093,0.13814]}],"total_contact_groups":4},"final_pose_error":0.10248,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48093,-0.01612,0.025],"final_tcp_position":[0.5022,0.03518,0.16505],"realised_fixture_position":[0.48093,-0.01612,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48093,-0.01612,0.08]},"phases":[{"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.50343,-0.0,0.33877],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.25879,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","subtask_id":"approach_socket","tcp_end":[0.49918,-1e-05,0.299],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50356,-0.0,0.33872],"object_pos_start":[0.50343,-0.0,0.33877],"object_to_goal_dist_end":0.25875,"object_to_goal_dist_start":0.25879,"object_z_max":0.33877,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","subtask_id":"approach_socket","tcp_end":[0.49928,-1e-05,0.29895],"tcp_start":[0.49918,-1e-05,0.299],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51078,-0.00598,0.12387],"object_pos_start":[0.50356,-0.0,0.33872],"object_to_goal_dist_end":0.04557,"object_to_goal_dist_start":0.25875,"object_z_max":0.34149,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"insert_peg","tcp_end":[0.47275,-0.00669,0.13626],"tcp_start":[0.49928,-1e-05,0.29895],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.5323,0.01999,0.14353],"object_pos_start":[0.51078,-0.00598,0.12387],"object_to_goal_dist_end":0.07402,"object_to_goal_dist_start":0.04557,"object_z_max":0.14214,"phase_name":"align_2","phase_peak_obstacle_force":0.0,"phase_type":"align","subtask_id":"insert_peg","tcp_end":[0.5022,0.03518,0.16505],"tcp_start":[0.47275,-0.00669,0.13626],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `d263ae29be72790e561c8447b0a7b2ba7baa0aae40b60396cc4b2e04f6cc146d`; realized-scene SHA-256: `b2240da92884894b1100a1c972a50aa9dbe8b49daf4551e90009b821f1d87f37`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.46685,-0.02106,0.025]},{"name":"target","value":[0.46685,-0.02106,0.025]},{"name":"socket","value":[0.46685,-0.02106,0.025]},{"name":"goal","value":[0.46685,-0.02106,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,-0.02106,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.46685,-0.02106,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.21053,"average_solve_count":76.0,"average_success_count":76.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00695,"align_1.lateral_offset_y":-0.00684,"align_2.lateral_offset_x":0.004,"align_2.lateral_offset_y":-0.00482,"push_1.push_distance":0.19903},"optimized_scores":{"best_composite_score":0.52495,"best_fitness_score":0.83495,"best_task_score":0.83495},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":907.0,"contact_point_centroid":[0.52667,-0.00802,0.06888],"force_p95":338.45533,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":930.30441,"mean_force":313.64942,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.45872,-0.00516,0.11991]},{"body_a":"world","body_b":"link6","contact_count":412.0,"contact_point_centroid":[0.67209,-0.0113,-8e-05],"force_p95":423.4203,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":735.61825,"mean_force":204.08894,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.46729,-0.01737,0.13847]},{"body_a":"attachment","body_b":"peg_socket","contact_count":5.0,"contact_point_centroid":[0.44632,0.00924,0.07974],"force_p95":702.64086,"geom_a":"peg_tip","geom_b":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":710.30352,"mean_force":395.25415,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.44359,-0.00198,0.08857]},{"body_a":"peg_socket","body_b":"link7","contact_count":282.0,"contact_point_centroid":[0.52677,-0.01196,0.06692],"force_p95":346.51471,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":479.76385,"mean_force":316.00719,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.46329,-0.01013,0.12549]},{"body_a":"world","body_b":"link6","contact_count":367.0,"contact_point_centroid":[0.67792,-0.00432,-1e-05],"force_p95":104.39534,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":237.9823,"mean_force":38.99919,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46291,-0.00547,0.12432]},{"body_a":"attachment","body_b":"peg_socket","contact_count":5.0,"contact_point_centroid":[0.43672,0.0054,0.07997],"force_p95":50.84939,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":56.78631,"mean_force":17.12505,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.43509,-0.00657,0.0888]}],"total_contact_groups":6},"final_pose_error":0.09433,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.47954,-0.03507,0.17347],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"phases":[{"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.50343,-0.0,0.33877],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.25879,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","subtask_id":"approach_socket","tcp_end":[0.49918,-1e-05,0.299],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50356,-0.0,0.33872],"object_pos_start":[0.50343,-0.0,0.33877],"object_to_goal_dist_end":0.25875,"object_to_goal_dist_start":0.25879,"object_z_max":0.33877,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","subtask_id":"approach_socket","tcp_end":[0.49928,-1e-05,0.29895],"tcp_start":[0.49918,-1e-05,0.299],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49995,-0.00681,0.10893],"object_pos_start":[0.50356,-0.0,0.33872],"object_to_goal_dist_end":0.02972,"object_to_goal_dist_start":0.25875,"object_z_max":0.34144,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"insert_peg","tcp_end":[0.46258,-0.00734,0.12319],"tcp_start":[0.49928,-1e-05,0.29895],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":523.0,"n_steps_budget":600.0,"object_pos_end":[0.51199,-0.03248,0.15022],"object_pos_start":[0.49995,-0.00681,0.10893],"object_to_goal_dist_end":0.0783,"object_to_goal_dist_start":0.02972,"object_z_max":0.15032,"phase_name":"align_2","phase_peak_obstacle_force":0.0,"phase_type":"align","subtask_id":"insert_peg","tcp_end":[0.47954,-0.03507,0.17347],"tcp_start":[0.46258,-0.00734,0.12319],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```