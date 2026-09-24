## Search State

- **Seed**: 8
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → align → contact → insert | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 4 | 0.4593 | 0.85 | ❌ rejected |
| 8 | approach → approach → contact → insert | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 3 | 0.2767 | 0.56 | ❌ rejected |
| 7 | approach → contact → insert | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | force_exceeded | 5 | 0.7379 | 0.86 | ❌ rejected |
| 6 | approach → align → contact → insert | joint_interpolation | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | 6 | -0.0933 | 0.65 | ❌ rejected |
| 5 | approach → approach → contact → insert | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | 3 | 0.4838 | 0.86 | ✅ accepted |

**Proposal policy**: task_score is 0.85 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `b9bf2317193e958308a6e071da8e3f166f4f6aad2cd63fb849fb719630631480`
- Frozen object start: [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]
- Frozen task target: [0.48615778212844485, 0.03898214746703404, 0.08]
- Frozen socket pose: [0.48615778212844485, 0.03898214746703404, 0.025] (static fixture for this episode)
- Goal object position: (0.48615778212844485, 0.03898214746703404, 0.025)
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
  frozen_task_target: [0.4862, 0.039, 0.08]
  frozen_socket_position: [0.4862, 0.039, 0.025]
  socket_state: static_frozen
  frozen_object_starts: {'peg': [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]}
  frozen_targets: {'socket_entry': [0.48615778212844485, 0.03898214746703404, 0.08]}
  frozen_fixtures: {'peg_socket': [0.48615778212844485, 0.03898214746703404, 0.025]}
  insertion_axis: [0, 0, -1]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  hole_depth_m: 0.05
  force_scale_n: 5
  realized_scene_sha256: b9bf2317193e958308a6e071da8e3f166f4f6aad2cd63fb849fb719630631480

## Subtask Layer

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| align | object | (0.00, 0.00, 0.12) | distance | — |
| approach | object | (0.00, 0.00, 0.09) | distance | — |
| contact | object | (0.00, 0.00, 0.07) | distance | — |
| insert | object | (0.00, 0.00, 0.06) | distance | — |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=0.459) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.12
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.1
- id: approach_2
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.04
    orientation:
      mode: keep_current
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - -0.01
    orientation:
      mode: keep_current
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
- id: insert_1
  type: insert
  generator: impedance_motion
  control: impedance_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.04
      axis: world_z
      mode: replace_offset_projection
      sign: negative
    orientation:
      mode: keep_current
  parameters:
    insert_speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
    insertion_distance:
      type: scalar
      range:
      - 0.01
      - 0.15
      default: 0.04
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.12]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings: none
- **approach_2** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.04]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, -0.01]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
- **insert_1** (`insert`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.04, mode=replace_offset_projection, sign=negative}
  - orientation: mode=keep_current
  - parameter_bindings:
    - insert_speed: status=consumed; consumers=generator.speed (replace)
    - insertion_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)

## Design Metrics

- **Composite score**: 0.459
- **task_score** (E): 0.855
- **fitness_score**: 0.386  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.260

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_high | 0.33 | 1.00 | 0.1191 |
| align | 0.00 | 1.00 | 0.1123 |
| contact | 1.00 | 1.00 | 0.0002 |
| insert | 1.00 | 0.00 | 0.0779 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_high | approach | 0.33 / step_budget | (0.500, -0.000, 0.301)→(0.505, -0.005, 0.192) | (0.504, -0.000, 0.340)→(0.536, -0.011, 0.173) | 0.260→0.101 | 1.00 / 1.000 | 288.295 | 1883.833 |
| align | align | 0.00 / step_budget | (0.505, -0.005, 0.192)→(0.563, 0.005, 0.257) | (0.536, -0.011, 0.173)→(0.577, 0.009, 0.222) | 0.101→0.176 | 1.00 / 2.000 | 644.011 | 2705.466 |
| contact | contact | 1.00 / force_exceeded | (0.563, 0.005, 0.257)→(0.563, 0.005, 0.258) | (0.577, 0.009, 0.222)→(0.577, 0.009, 0.222) | 0.176→0.177 | 1.00 / 2.000 | 287.093 | 359.549 |
| insert | insert | 1.00 / time_limit | (0.563, 0.005, 0.258)→(0.563, 0.005, 0.335) | (0.577, 0.009, 0.222)→(0.577, 0.009, 0.299) | 0.177→0.243 | 0.00 / 0.000 | 0.000 | 133.634 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.848
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.848
- phase_score: 0.088
- phase_breakdown.insert_score: 0.159
- phase_breakdown.approach_score: 0.003
- phase_breakdown.contact_score: 0.035
- phase_breakdown.align_score: 0.011

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.392
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.864
- **Median Q (composite search score)**: 0.461
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.445


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `111371231b67e0c9737e2a991f4190656c428bca2212422046741d75dd4bee83`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `33ad86acc0270e6e89309305f52a6240db2b433d70da525d7c59722b30949f46`; realized-scene SHA-256: `b9bf2317193e958308a6e071da8e3f166f4f6aad2cd63fb849fb719630631480`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.48616,0.03898,0.025]},{"name":"target","value":[0.48616,0.03898,0.025]},{"name":"socket","value":[0.48616,0.03898,0.025]},{"name":"goal","value":[0.48616,0.03898,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.03898,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.48616,0.03898,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.73118,"average_solve_count":93.0,"average_success_count":93.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact.contact_force":10.13642,"insert.insert_speed":0.0498,"insert.insertion_distance":0.14931,"insert.max_insert_time":5.8107},"optimized_scores":{"best_composite_score":0.46518,"best_fitness_score":0.39185,"best_task_score":0.84752},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link5","contact_count":80.0,"contact_point_centroid":[0.55191,0.15496,-0.00016],"force_p95":4525.79303,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":5303.11845,"mean_force":1742.68699,"phase_index":1.0,"phase_name":"align","phase_type":"align","tcp_position_centroid":[0.54122,0.02653,0.23472]},{"body_a":"peg_socket","body_b":"link5","contact_count":76.0,"contact_point_centroid":[0.52996,0.09822,0.05387],"force_p95":3605.93722,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3719.8471,"mean_force":1383.63179,"phase_index":1.0,"phase_name":"align","phase_type":"align","tcp_position_centroid":[0.54134,0.02841,0.23664]},{"body_a":"attachment","body_b":"peg_socket","contact_count":10.0,"contact_point_centroid":[0.45447,0.00882,0.07945],"force_p95":3349.49227,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3382.3713,"mean_force":1416.43598,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.45048,0.00413,0.0917]},{"body_a":"attachment","body_b":"peg_socket","contact_count":14.0,"contact_point_centroid":[0.45881,0.00409,0.07872],"force_p95":2983.61376,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3009.5933,"mean_force":1194.72862,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.453,0.00416,0.09131]},{"body_a":"peg_socket","body_b":"link5","contact_count":69.0,"contact_point_centroid":[0.53207,0.09815,0.04946],"force_p95":2234.03857,"geom_a":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2924.22444,"mean_force":435.85391,"phase_index":1.0,"phase_name":"align","phase_type":"align","tcp_position_centroid":[0.54164,0.02765,0.23615]},{"body_a":"peg_socket","body_b":"link7","contact_count":840.0,"contact_point_centroid":[0.54603,0.0101,0.0799],"force_p95":299.45044,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":737.69124,"mean_force":286.52871,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.46764,0.00391,0.12788]},{"body_a":"world","body_b":"link5","contact_count":2.0,"contact_point_centroid":[0.54173,0.15573,-0.0001],"force_p95":642.35625,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":653.22456,"mean_force":544.54143,"phase_index":2.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.54032,0.052,0.25053]},{"body_a":"world","body_b":"link6","contact_count":20.0,"contact_point_centroid":[0.67178,0.08872,-0.00083],"force_p95":502.44394,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":527.41561,"mean_force":299.68249,"phase_index":1.0,"phase_name":"align","phase_type":"align","tcp_position_centroid":[0.52172,-0.01997,0.17611]},{"body_a":"peg_socket","body_b":"link7","contact_count":384.0,"contact_point_centroid":[0.54601,0.02567,0.07995],"force_p95":400.72297,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":453.36248,"mean_force":335.10179,"phase_index":1.0,"phase_name":"align","phase_type":"align","tcp_position_centroid":[0.48009,-0.00869,0.13799]},{"body_a":"peg_socket","body_b":"link5","contact_count":2.0,"contact_point_centroid":[0.52631,0.09887,0.05985],"force_p95":311.97776,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":327.59428,"mean_force":171.42906,"phase_index":2.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.54032,0.052,0.25053]},{"body_a":"world","body_b":"link5","contact_count":3.0,"contact_point_centroid":[0.54174,0.1559,-4e-05],"force_p95":188.49111,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":197.66974,"mean_force":115.02266,"phase_index":3.0,"phase_name":"insert","phase_type":"insert","tcp_position_centroid":[0.54043,0.05229,0.2507]},{"body_a":"peg_socket","body_b":"link5","contact_count":477.0,"contact_point_centroid":[0.52704,0.09897,0.07118],"force_p95":90.80698,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":148.94528,"mean_force":51.23497,"phase_index":3.0,"phase_name":"insert","phase_type":"insert","tcp_position_centroid":[0.53905,0.05456,0.27226]},{"body_a":"peg_socket","body_b":"link5","contact_count":1.0,"contact_point_centroid":[0.53043,0.09897,0.05],"force_p95":0.0,"geom_a":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.54028,0.05193,0.25048]}],"total_contact_groups":13},"final_pose_error":0.07137,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.54006,0.05218,0.32861],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"peak_contact_force":5303.11845,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":933.0,"n_steps_budget":1000.0,"object_pos_end":[0.50992,0.00936,0.12594],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.04792,"object_to_goal_dist_start":0.26034,"object_z_max":0.34442,"peak_contact_force":296.44361,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":864.0,"raw_peak_contact_force":3382.3713,"subtask_id":"approach","tcp_end":[0.47105,0.00503,0.13434],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.56103,0.06333,0.21824],"object_pos_start":[0.50992,0.00936,0.12594],"object_to_goal_dist_end":0.16385,"object_to_goal_dist_start":0.04792,"object_z_max":0.21808,"peak_contact_force":592.07592,"phase_name":"align","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":629.0,"raw_peak_contact_force":5303.11845,"subtask_id":"align","tcp_end":[0.54028,0.05193,0.25048],"tcp_start":[0.47105,0.00503,0.13434],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.56116,0.06362,0.21842],"object_pos_start":[0.56103,0.06333,0.21824],"object_to_goal_dist_end":0.16416,"object_to_goal_dist_start":0.16385,"object_z_max":0.21835,"peak_contact_force":435.8583,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":5.0,"raw_peak_contact_force":653.22456,"subtask_id":"contact","tcp_end":[0.54042,0.0522,0.25066],"tcp_start":[0.54028,0.05193,0.25048],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56038,0.06349,0.29606],"object_pos_start":[0.56116,0.06362,0.21842],"object_to_goal_dist_end":0.23314,"object_to_goal_dist_start":0.16416,"object_z_max":0.29596,"peak_contact_force":0.0,"phase_name":"insert","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":480.0,"raw_peak_contact_force":197.66974,"subtask_id":"insert","tcp_end":[0.54006,0.05218,0.32861],"tcp_start":[0.54042,0.0522,0.25066],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `7e8ba2d913c6be5a5528190a0c7ff1e14947b230e7e2c93846f050bf72228229`; realized-scene SHA-256: `d30c452da2a3cff083d30694df03632a9bb782339e47c14383f7124ad9a32464`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.52962,-0.01705,0.025]},{"name":"target","value":[0.52962,-0.01705,0.025]},{"name":"socket","value":[0.52962,-0.01705,0.025]},{"name":"goal","value":[0.52962,-0.01705,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,-0.01705,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.52962,-0.01705,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.69892,"average_solve_count":93.0,"average_success_count":93.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact.contact_force":2.54571,"insert.insert_speed":0.04977,"insert.insertion_distance":0.14129,"insert.max_insert_time":14.70744},"optimized_scores":{"best_composite_score":0.46103,"best_fitness_score":0.3877,"best_task_score":0.8526},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link5","contact_count":247.0,"contact_point_centroid":[0.51526,0.09212,-6e-05],"force_p95":812.31472,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1638.1485,"mean_force":481.18068,"phase_index":1.0,"phase_name":"align","phase_type":"align","tcp_position_centroid":[0.56801,0.04062,0.26035]},{"body_a":"peg_socket","body_b":"link5","contact_count":239.0,"contact_point_centroid":[0.51482,0.04266,0.05935],"force_p95":756.49381,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1428.56922,"mean_force":285.37591,"phase_index":1.0,"phase_name":"align","phase_type":"align","tcp_position_centroid":[0.56699,0.03738,0.26016]},{"body_a":"peg_socket","body_b":"link6","contact_count":173.0,"contact_point_centroid":[0.58954,-0.0139,0.0799],"force_p95":503.75854,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1337.56043,"mean_force":337.60836,"phase_index":1.0,"phase_name":"align","phase_type":"align","tcp_position_centroid":[0.49052,-0.04678,0.21467]},{"body_a":"peg_socket","body_b":"link7","contact_count":78.0,"contact_point_centroid":[0.5779,-0.00916,0.07919],"force_p95":590.19154,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1216.07161,"mean_force":276.22244,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.47058,-0.00383,0.14837]},{"body_a":"peg_socket","body_b":"link6","contact_count":740.0,"contact_point_centroid":[0.58927,-0.00689,0.07983],"force_p95":302.44377,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":841.79685,"mean_force":250.7263,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.46118,-0.00519,0.17178]},{"body_a":"attachment","body_b":"peg_socket","contact_count":2.0,"contact_point_centroid":[0.46967,-0.00157,0.07987],"force_p95":806.30043,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":807.46308,"mean_force":795.83663,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.46132,-0.00157,0.09256]},{"body_a":"peg_socket","body_b":"link7","contact_count":24.0,"contact_point_centroid":[0.53714,0.01368,0.078],"force_p95":436.18118,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":689.32131,"mean_force":84.07739,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.44216,-0.00206,0.1024]},{"body_a":"peg_socket","body_b":"link7","contact_count":17.0,"contact_point_centroid":[0.58958,-0.03107,0.07991],"force_p95":492.0766,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":508.5536,"mean_force":422.34362,"phase_index":1.0,"phase_name":"align","phase_type":"align","tcp_position_centroid":[0.4938,-0.00509,0.17686]},{"body_a":"peg_socket","body_b":"link5","contact_count":24.0,"contact_point_centroid":[0.52452,0.0416,0.04961],"force_p95":349.72817,"geom_a":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":363.58628,"mean_force":250.4697,"phase_index":1.0,"phase_name":"align","phase_type":"align","tcp_position_centroid":[0.55949,0.00931,0.25807]},{"body_a":"peg_socket","body_b":"link7","contact_count":25.0,"contact_point_centroid":[0.53091,-0.07416,0.07988],"force_p95":247.54365,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":279.4408,"mean_force":125.80981,"phase_index":1.0,"phase_name":"align","phase_type":"align","tcp_position_centroid":[0.48365,-0.03397,0.20477]},{"body_a":"world","body_b":"link5","contact_count":2.0,"contact_point_centroid":[0.51929,0.0901,-3e-05],"force_p95":206.4357,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":212.12265,"mean_force":155.25312,"phase_index":2.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.57248,0.04568,0.26106]},{"body_a":"peg_socket","body_b":"link5","contact_count":1.0,"contact_point_centroid":[0.5185,0.04294,0.06121],"force_p95":185.80631,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":185.80631,"mean_force":185.80631,"phase_index":2.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.57249,0.04568,0.26108]},{"body_a":"peg_socket","body_b":"link5","contact_count":292.0,"contact_point_centroid":[0.51354,0.04294,0.07371],"force_p95":37.50805,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":98.69575,"mean_force":24.38679,"phase_index":3.0,"phase_name":"insert","phase_type":"insert","tcp_position_centroid":[0.57166,0.04651,0.27714]},{"body_a":"world","body_b":"link5","contact_count":1.0,"contact_point_centroid":[0.51936,0.09009,-1e-05],"force_p95":77.39277,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":77.39277,"mean_force":77.39277,"phase_index":3.0,"phase_name":"insert","phase_type":"insert","tcp_position_centroid":[0.5725,0.04567,0.26111]},{"body_a":"peg_socket","body_b":"link7","contact_count":14.0,"contact_point_centroid":[0.53791,-0.04722,0.07903],"force_p95":0.0,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.44149,-0.00202,0.09805]}],"total_contact_groups":15},"final_pose_error":0.06352,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.5722,0.046,0.33888],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":1638.1485,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":932.0,"n_steps_budget":990.0,"object_pos_end":[0.52874,-0.00823,0.15857],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.08406,"object_to_goal_dist_start":0.26034,"object_z_max":0.34451,"peak_contact_force":321.26557,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":858.0,"raw_peak_contact_force":1216.07161,"subtask_id":"approach","tcp_end":[0.49346,-0.00079,0.17588],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.5838,0.05432,0.22367],"object_pos_start":[0.52874,-0.00823,0.15857],"object_to_goal_dist_end":0.17496,"object_to_goal_dist_start":0.08406,"object_z_max":0.22364,"peak_contact_force":827.60493,"phase_name":"align","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":725.0,"raw_peak_contact_force":1638.1485,"subtask_id":"align","tcp_end":[0.57247,0.04568,0.26105],"tcp_start":[0.49346,-0.00079,0.17588],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.58383,0.0543,0.22374],"object_pos_start":[0.5838,0.05432,0.22367],"object_to_goal_dist_end":0.17503,"object_to_goal_dist_start":0.17496,"object_z_max":0.2237,"peak_contact_force":212.12265,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3.0,"raw_peak_contact_force":212.12265,"subtask_id":"contact","tcp_end":[0.5725,0.04567,0.26111],"tcp_start":[0.57247,0.04568,0.26105],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58309,0.0545,0.30134],"object_pos_start":[0.58383,0.0543,0.22374],"object_to_goal_dist_end":0.24263,"object_to_goal_dist_start":0.17503,"object_z_max":0.30125,"peak_contact_force":0.0,"phase_name":"insert","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":293.0,"raw_peak_contact_force":98.69575,"subtask_id":"insert","tcp_end":[0.5722,0.046,0.33888],"tcp_start":[0.5725,0.04567,0.26111],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `6bfe353c76201464a4c9772ff30fffbe6279f45f6a3eb14a1a3a1447c56a946a`; realized-scene SHA-256: `3df42339bb213b8d34da19ed0076dd8b56ad93b79493c43fb7ab2bb6b5f8a158`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.53648,-0.02339,0.025]},{"name":"target","value":[0.53648,-0.02339,0.025]},{"name":"socket","value":[0.53648,-0.02339,0.025]},{"name":"goal","value":[0.53648,-0.02339,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.53648,-0.02339,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.53648,-0.02339,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.90741,"average_solve_count":108.0,"average_success_count":108.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact.contact_force":10.92126,"insert.insert_speed":0.04997,"insert.insertion_distance":0.1222,"insert.max_insert_time":11.71421},"optimized_scores":{"best_composite_score":0.45171,"best_fitness_score":0.37837,"best_task_score":0.86351},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":744.0,"contact_point_centroid":[0.59379,-0.13148,-7e-05],"force_p95":757.41892,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1175.13184,"mean_force":345.83451,"phase_index":1.0,"phase_name":"align","phase_type":"align","tcp_position_centroid":[0.59038,-0.12884,0.26812]},{"body_a":"peg_socket","body_b":"link7","contact_count":29.0,"contact_point_centroid":[0.54535,0.00732,0.07767],"force_p95":820.89456,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1053.05681,"mean_force":207.29381,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.44977,-0.0033,0.10245]},{"body_a":"peg_socket","body_b":"link6","contact_count":326.0,"contact_point_centroid":[0.59648,-0.08334,0.04276],"force_p95":448.77722,"geom_a":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":995.26664,"mean_force":253.27511,"phase_index":1.0,"phase_name":"align","phase_type":"align","tcp_position_centroid":[0.59339,-0.14779,0.26919]},{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.47655,-0.00274,0.07982],"force_p95":847.13724,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":849.62837,"mean_force":420.66231,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.45895,-0.0027,0.08934]},{"body_a":"peg_socket","body_b":"link6","contact_count":785.0,"contact_point_centroid":[0.59613,-0.01405,0.0798],"force_p95":332.52446,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":676.10645,"mean_force":254.27296,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.46865,-0.00747,0.17299]},{"body_a":"peg_socket","body_b":"link6","contact_count":591.0,"contact_point_centroid":[0.59646,-0.08333,0.07704],"force_p95":392.42107,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":429.71719,"mean_force":254.79011,"phase_index":1.0,"phase_name":"align","phase_type":"align","tcp_position_centroid":[0.58932,-0.1084,0.27416]},{"body_a":"peg_socket","body_b":"link7","contact_count":30.0,"contact_point_centroid":[0.56674,-0.00319,0.07855],"force_p95":235.66838,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":274.55671,"mean_force":58.98188,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.44961,-0.00335,0.10414]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.59645,-0.08332,0.07998],"force_p95":213.29831,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":213.29831,"mean_force":213.29831,"phase_index":2.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.57725,-0.08286,0.26075]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.62131,-0.12373,-0.00011],"force_p95":173.38929,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":173.38929,"mean_force":173.38929,"phase_index":2.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.57725,-0.08286,0.26075]},{"body_a":"peg_socket","body_b":"link6","contact_count":55.0,"contact_point_centroid":[0.59647,-0.08336,0.07999],"force_p95":79.10448,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":104.53594,"mean_force":26.88854,"phase_index":3.0,"phase_name":"insert","phase_type":"insert","tcp_position_centroid":[0.57697,-0.08337,0.26245]},{"body_a":"world","body_b":"link6","contact_count":4.0,"contact_point_centroid":[0.6214,-0.12389,-6e-05],"force_p95":97.7938,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":97.82057,"mean_force":72.24941,"phase_index":3.0,"phase_name":"insert","phase_type":"insert","tcp_position_centroid":[0.57735,-0.083,0.26083]},{"body_a":"peg_socket","body_b":"link7","contact_count":10.0,"contact_point_centroid":[0.54573,-0.05348,0.07943],"force_p95":0.0,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.44873,-0.00313,0.0947]}],"total_contact_groups":12},"final_pose_error":0.04423,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53648,-0.02339,0.025],"final_tcp_position":[0.57704,-0.08324,0.33874],"realised_fixture_position":[0.53648,-0.02339,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53648,-0.02339,0.08]},"peak_contact_force":1175.13184,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":933.0,"n_steps_budget":1000.0,"object_pos_end":[0.5687,-0.03368,0.23408],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.17203,"object_to_goal_dist_start":0.26034,"object_z_max":0.34477,"peak_contact_force":247.17679,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":858.0,"raw_peak_contact_force":1053.05681,"subtask_id":"approach","tcp_end":[0.55008,-0.02013,0.26679],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58714,-0.09078,0.22281],"object_pos_start":[0.5687,-0.03368,0.23408],"object_to_goal_dist_end":0.19034,"object_to_goal_dist_start":0.17203,"object_z_max":0.25691,"peak_contact_force":512.35301,"phase_name":"align","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1661.0,"raw_peak_contact_force":1175.13184,"subtask_id":"align","tcp_end":[0.57725,-0.08286,0.26075],"tcp_start":[0.55008,-0.02013,0.26679],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.58721,-0.09083,0.22283],"object_pos_start":[0.58714,-0.09078,0.22281],"object_to_goal_dist_end":0.19041,"object_to_goal_dist_start":0.19034,"object_z_max":0.22281,"peak_contact_force":213.29831,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":213.29831,"subtask_id":"contact","tcp_end":[0.57733,-0.08291,0.26077],"tcp_start":[0.57725,-0.08286,0.26075],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58646,-0.09099,0.30065],"object_pos_start":[0.58721,-0.09083,0.22283],"object_to_goal_dist_end":0.25385,"object_to_goal_dist_start":0.19041,"object_z_max":0.30055,"peak_contact_force":0.0,"phase_name":"insert","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":59.0,"raw_peak_contact_force":104.53594,"subtask_id":"insert","tcp_end":[0.57704,-0.08324,0.33874],"tcp_start":[0.57733,-0.08291,0.26077],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```