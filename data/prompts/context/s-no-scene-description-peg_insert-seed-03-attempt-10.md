## Search State

- **Seed**: 3
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → pull | linear_cartesian | linear_cartesian | arc_cartesian | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 3 | 0.6763 | 0.86 | ❌ rejected |
| 9 | rotate → retract → descend → pull | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | 0.7628 | 0.97 | ✅ accepted |
| 8 | rotate → retract → descend → pull | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | 0.7627 | 0.97 | ✅ accepted |
| 7 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | admittance_control | pose_tolerance | force_exceeded | force_exceeded | 6 | 1.2189 | 0.88 | ❌ rejected |
| 6 | approach → retract → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.3242 | 0.82 | ❌ rejected |

**Proposal policy**: task_score is 0.86 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 40.0 N
- Primary evaluation target: **insertion depth ratio (axial progress into hole)**

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
| `object` | offset from object initial position | approach/contact targets near object start |
| `goal` | offset from task goal position | final destination targets |
| `fixture` | offset from fixture pose | approach/contact targets near fixture |

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

## Current Skill (Q=0.676) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
phases:
- id: rotate_1
  type: rotate
  generator: impedance_motion
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: none
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.1
      axis: world_z
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.05
      axis: world_z
      mode: add_to_offset
      sign: negative
    orientation:
      mode: keep_current
  parameters:
    depth:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
- id: pull_1
  type: pull
  generator: arc_cartesian
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.1
      axis: world_z
      mode: add_to_offset
      sign: negative
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    pull_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **rotate_1** (`rotate`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=none
  - parameter_bindings: none
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.1, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.05, mode=add_to_offset, sign=negative}
  - orientation: mode=keep_current
  - parameter_bindings:
    - depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **pull_1** (`pull`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.1, mode=add_to_offset, sign=negative}
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - pull_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)

## Design Metrics

- **Composite score**: 0.676
- **task_score** (E): 0.856
- **fitness_score**: 0.856  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.180

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.33 | 1.00 | 0.1395 |
| descend_1 | 0.33 | 1.00 | 0.0145 |
| pull_1 | 1.00 | 1.00 | 0.1517 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.33 / step_budget | (0.500, -0.000, 0.301)→(0.465, 0.004, 0.166) | (0.504, -0.000, 0.340)→(0.501, 0.003, 0.150) | 0.260→0.071 | 1.00 / 1.000 | 291.410 | 1619.260 |
| descend_1 | descend | 0.33 / step_budget | (0.465, 0.004, 0.166)→(0.476, 0.003, 0.175) | (0.501, 0.003, 0.150)→(0.511, 0.003, 0.157) | 0.071→0.078 | 1.00 / 1.000 | 228.163 | 440.924 |
| pull_1 | pull | 1.00 / time_limit | (0.476, 0.003, 0.175)→(0.582, -0.032, 0.257) | (0.511, 0.003, 0.157)→(0.600, -0.032, 0.222) | 0.078→0.183 | 1.00 / 1.667 | 476.997 | 1353.858 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.871
- alignment_error: None
- force_efficiency: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.871
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.871
- **Median Q (composite search score)**: 0.684
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.288


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `2fc05e51a25fc23cdfa051e1c0c9cb8327fc4318047dd2c0794162fe696d964b`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `78de15924f40c9df864f10a8c33fe438e6928bbf6063e6b2cf47f87609839b79`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.27397,"average_solve_count":73.0,"average_success_count":73.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.08208,"descend_1.depth":0.03675,"pull_1.pull_distance":0.05294},"optimized_scores":{"best_composite_score":0.65471,"best_fitness_score":0.83471,"best_task_score":0.83471},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link5","contact_count":160.0,"contact_point_centroid":[0.53589,0.10357,-0.00013],"force_p95":1542.13702,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1627.66717,"mean_force":621.57607,"phase_index":2.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.53846,0.00956,0.2549]},{"body_a":"peg_socket","body_b":"link5","contact_count":94.0,"contact_point_centroid":[0.51733,0.03856,0.05997],"force_p95":1110.62052,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1136.5048,"mean_force":607.75903,"phase_index":2.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.54297,0.01716,0.26184]},{"body_a":"peg_socket","body_b":"link7","contact_count":748.0,"contact_point_centroid":[0.52663,-0.00937,0.06691],"force_p95":338.51684,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1057.74403,"mean_force":309.40246,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45649,-0.00597,0.11461]},{"body_a":"world","body_b":"link6","contact_count":386.0,"contact_point_centroid":[0.67501,-0.00611,-0.00018],"force_p95":368.55794,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":897.18778,"mean_force":228.26067,"phase_index":2.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.47462,-0.02126,0.14401]},{"body_a":"world","body_b":"link6","contact_count":423.0,"contact_point_centroid":[0.68173,-0.01201,-5e-05],"force_p95":284.29469,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":788.1603,"mean_force":271.04588,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46822,-0.00786,0.12668]},{"body_a":"attachment","body_b":"peg_socket","contact_count":6.0,"contact_point_centroid":[0.4422,0.00929,0.07979],"force_p95":612.42539,"geom_a":"peg_tip","geom_b":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":618.55478,"mean_force":330.07437,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44021,-0.00339,0.08657]},{"body_a":"peg_socket","body_b":"link7","contact_count":102.0,"contact_point_centroid":[0.52657,-0.01524,0.06702],"force_p95":438.19464,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":495.57928,"mean_force":329.57233,"phase_index":2.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.46261,-0.01546,0.12459]},{"body_a":"peg_socket","body_b":"link5","contact_count":93.0,"contact_point_centroid":[0.52373,0.03865,0.04999],"force_p95":416.81034,"geom_a":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":429.60479,"mean_force":159.58032,"phase_index":2.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.54298,0.0172,0.26185]},{"body_a":"peg_socket","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.52679,-0.01195,0.06377],"force_p95":285.62367,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":303.43406,"mean_force":143.01968,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46201,-0.00706,0.11998]},{"body_a":"world","body_b":"link6","contact_count":74.0,"contact_point_centroid":[0.67914,-0.00946,-3e-05],"force_p95":115.67108,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":143.01583,"mean_force":38.32011,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46209,-0.00683,0.12067]},{"body_a":"attachment","body_b":"peg_socket","contact_count":10.0,"contact_point_centroid":[0.43627,0.00725,0.07988],"force_p95":0.0,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.43449,-0.00594,0.08669]}],"total_contact_groups":11},"final_pose_error":0.25041,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.54339,0.01849,0.26218],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"peak_contact_force":1627.66717,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":842.0,"n_steps_budget":900.0,"object_pos_end":[0.49952,-0.00821,0.10626],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.02751,"object_to_goal_dist_start":0.26034,"object_z_max":0.34436,"peak_contact_force":334.80095,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":838.0,"raw_peak_contact_force":1057.74403,"tcp_end":[0.46196,-0.00702,0.11995],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":426.0,"n_steps_budget":600.0,"object_pos_end":[0.50942,-0.00943,0.11642],"object_pos_start":[0.49952,-0.00821,0.10626],"object_to_goal_dist_end":0.03878,"object_to_goal_dist_start":0.02751,"object_z_max":0.11641,"peak_contact_force":265.59167,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":431.0,"raw_peak_contact_force":788.1603,"tcp_end":[0.47271,-0.00845,0.13227],"tcp_start":[0.46196,-0.00702,0.11995],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":654.0,"n_steps_budget":690.0,"object_pos_end":[0.56153,0.0262,0.22737],"object_pos_start":[0.50942,-0.00943,0.11642],"object_to_goal_dist_end":0.16184,"object_to_goal_dist_start":0.03878,"object_z_max":0.22737,"peak_contact_force":502.85636,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":835.0,"raw_peak_contact_force":1627.66717,"tcp_end":[0.54339,0.01849,0.26218],"tcp_start":[0.47271,-0.00845,0.13227],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `23bedb35dfb8044c9064b13b9f8101cd4e2be35581b8354b6b999b22e5fca070`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":8.0,"average_failure_rate":0.09524,"average_mean_iterations":24.65476,"average_solve_count":84.0,"average_success_count":76.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.1339,"descend_1.depth":0.03257,"pull_1.pull_distance":0.09781},"optimized_scores":{"best_composite_score":0.69055,"best_fitness_score":0.87055,"best_task_score":0.87055},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":86.0,"contact_point_centroid":[0.68582,-0.09971,-0.00021],"force_p95":793.69981,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1260.00082,"mean_force":536.04214,"phase_index":2.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.60818,-0.06909,0.25497]},{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.47561,6e-05,0.07959],"force_p95":979.08836,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1001.03639,"mean_force":797.76723,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46584,8e-05,0.09151]},{"body_a":"peg_socket","body_b":"link7","contact_count":24.0,"contact_point_centroid":[0.56731,0.00126,0.0796],"force_p95":799.98214,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":891.88242,"mean_force":311.72907,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44733,-1e-05,0.1086]},{"body_a":"peg_socket","body_b":"link6","contact_count":846.0,"contact_point_centroid":[0.59534,-0.01273,0.07905],"force_p95":379.66686,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":592.32305,"mean_force":272.97676,"phase_index":2.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.50677,-0.00601,0.21899]},{"body_a":"peg_socket","body_b":"link6","contact_count":396.0,"contact_point_centroid":[0.59518,-0.00275,0.07983],"force_p95":273.45734,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":402.45382,"mean_force":237.74806,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45682,0.00022,0.16993]},{"body_a":"peg_socket","body_b":"link6","contact_count":422.0,"contact_point_centroid":[0.59542,-0.0025,0.07995],"force_p95":214.09054,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":252.8629,"mean_force":193.0076,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47526,0.00065,0.19754]},{"body_a":"peg_socket","body_b":"link7","contact_count":10.0,"contact_point_centroid":[0.54744,-0.02918,0.07948],"force_p95":116.6518,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":132.83559,"mean_force":26.54104,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4501,-3e-05,0.09819]}],"total_contact_groups":7},"final_pose_error":0.29168,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.61524,-0.06721,0.25435],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"peak_contact_force":1260.00082,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.506,0.00063,0.1771],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.09729,"object_to_goal_dist_start":0.26034,"object_z_max":0.34482,"peak_contact_force":245.7261,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":434.0,"raw_peak_contact_force":1001.03639,"tcp_end":[0.47068,0.00062,0.19588],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":426.0,"n_steps_budget":600.0,"object_pos_end":[0.51304,0.00067,0.1794],"object_pos_start":[0.506,0.00063,0.1771],"object_to_goal_dist_end":0.10025,"object_to_goal_dist_start":0.09729,"object_z_max":0.17939,"peak_contact_force":209.61884,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":422.0,"raw_peak_contact_force":252.8629,"tcp_end":[0.47856,0.00066,0.19968],"tcp_start":[0.47068,0.00062,0.19588],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.63206,-0.07203,0.21838],"object_pos_start":[0.51304,0.00067,0.1794],"object_to_goal_dist_end":0.2044,"object_to_goal_dist_start":0.10025,"object_z_max":0.24735,"peak_contact_force":466.40013,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":932.0,"raw_peak_contact_force":1260.00082,"tcp_end":[0.61524,-0.06721,0.25435],"tcp_start":[0.47856,0.00066,0.19968],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0b9f57c3f8a8fdb0f6fef54a4b5c0cfa6a2779a7721b018896a4efe993ac60cd`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":3.0,"average_failure_rate":0.03846,"average_mean_iterations":13.64103,"average_solve_count":78.0,"average_success_count":75.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13237,"descend_1.depth":0.06004,"pull_1.pull_distance":0.12116},"optimized_scores":{"best_composite_score":0.68364,"best_fitness_score":0.86364,"best_task_score":0.86364},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link6","contact_count":375.0,"contact_point_centroid":[0.58428,0.00955,0.07945],"force_p95":1653.04366,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2799.00096,"mean_force":423.04521,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45878,0.0107,0.15846]},{"body_a":"peg_socket","body_b":"link7","contact_count":215.0,"contact_point_centroid":[0.57971,0.01169,0.07957],"force_p95":2303.28576,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2795.99102,"mean_force":528.57276,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45959,0.00705,0.14335]},{"body_a":"world","body_b":"link6","contact_count":52.0,"contact_point_centroid":[0.66395,-0.07389,-0.00035],"force_p95":780.13364,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1173.9064,"mean_force":610.06657,"phase_index":2.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.58758,-0.04622,0.25541]},{"body_a":"attachment","body_b":"peg_socket","contact_count":11.0,"contact_point_centroid":[0.46633,0.00465,0.07852],"force_p95":1046.64585,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1087.28423,"mean_force":273.99286,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45938,0.00465,0.09052]},{"body_a":"peg_socket","body_b":"link7","contact_count":21.0,"contact_point_centroid":[0.55308,-0.00555,0.0788],"force_p95":738.1172,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":816.71248,"mean_force":333.74873,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45645,0.00525,0.09903]},{"body_a":"peg_socket","body_b":"link6","contact_count":893.0,"contact_point_centroid":[0.58429,0.00581,0.07976],"force_p95":388.34135,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":612.61359,"mean_force":283.89711,"phase_index":2.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.50508,0.01289,0.22163]},{"body_a":"peg_socket","body_b":"link7","contact_count":15.0,"contact_point_centroid":[0.58388,0.04583,0.07987],"force_p95":370.60068,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":371.87089,"mean_force":286.53815,"phase_index":2.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.4895,0.06207,0.18442]},{"body_a":"peg_socket","body_b":"link6","contact_count":481.0,"contact_point_centroid":[0.58437,0.0161,0.07993],"force_p95":222.12398,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":281.74811,"mean_force":206.93028,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46991,0.01795,0.18888]}],"total_contact_groups":8},"final_pose_error":0.31113,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.5244,0.02464,0.025],"final_tcp_position":[0.58862,-0.046,0.25497],"realised_fixture_position":[0.5244,0.02464,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.5244,0.02464,0.08]},"peak_contact_force":2799.00096,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.49894,0.01798,0.16598],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.08785,"object_to_goal_dist_start":0.26034,"object_z_max":0.34475,"peak_contact_force":293.70415,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":622.0,"raw_peak_contact_force":2799.00096,"tcp_end":[0.46243,0.01789,0.18231],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":484.0,"n_steps_budget":600.0,"object_pos_end":[0.51098,0.018,0.17399],"object_pos_start":[0.49894,0.01798,0.16598],"object_to_goal_dist_end":0.09633,"object_to_goal_dist_start":0.08785,"object_z_max":0.17398,"peak_contact_force":209.27707,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":481.0,"raw_peak_contact_force":281.74811,"tcp_end":[0.47648,0.01784,0.19424],"tcp_start":[0.46243,0.01789,0.18231],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60539,-0.04979,0.21886],"object_pos_start":[0.51098,0.018,0.17399],"object_to_goal_dist_end":0.18129,"object_to_goal_dist_start":0.09633,"object_z_max":0.24292,"peak_contact_force":461.73344,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":960.0,"raw_peak_contact_force":1173.9064,"tcp_end":[0.58862,-0.046,0.25497],"tcp_start":[0.47648,0.01784,0.19424],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```