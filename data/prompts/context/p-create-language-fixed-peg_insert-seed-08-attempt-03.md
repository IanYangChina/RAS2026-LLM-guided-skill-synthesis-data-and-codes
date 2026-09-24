## Search State

- **Seed**: 8
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → approach → contact → insert | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.4040 | 0.85 | ❌ rejected |
| 2 | approach → approach → contact → insert | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | position_control | force_threshold_switch | impedance_control | impedance_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 4 | 0.5834 | 0.84 | ❌ rejected |
| 1 | approach → approach → contact → insert | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | 3 | 0.3783 | 0.84 | ❌ rejected |
| 0 | approach → approach → contact → insert | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | 3 | 0.4827 | 0.86 | ✅ accepted |

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

## Current Skill (Q=0.404) — your mutation base

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

- **Composite score**: 0.404
- **task_score** (E): 0.849
- **fitness_score**: 0.414  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.260

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_align | 0.33 | 1.00 | 0.1234 |
| approach_descend | 0.33 | 0.67 | 0.0390 |
| contact_probe | 1.00 | 1.00 | 0.0083 |
| insert_peg | 0.00 | 0.00 | 0.1766 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_align | approach | 0.33 / step_budget | (0.500, -0.000, 0.301)→(0.463, -0.002, 0.185) | (0.504, -0.000, 0.340)→(0.498, -0.001, 0.167) | 0.260→0.089 | 1.00 / 1.333 | 263.397 | 1097.822 |
| approach_descend | approach | 0.33 / step_budget | (0.463, -0.002, 0.185)→(0.495, -0.002, 0.167) | (0.498, -0.001, 0.167)→(0.531, -0.002, 0.150) | 0.089→0.082 | 0.67 / 0.667 | 128.505 | 616.813 |
| contact_probe | contact | 1.00 / force_exceeded | (0.495, -0.002, 0.167)→(0.497, -0.009, 0.171) | (0.531, -0.002, 0.150)→(0.533, -0.010, 0.155) | 0.082→0.090 | 1.00 / 1.000 | 358.471 | 358.471 |
| insert_peg | insert | 0.00 / step_budget | (0.497, -0.009, 0.171)→(0.529, -0.015, 0.345) | (0.533, -0.010, 0.155)→(0.569, -0.016, 0.343) | 0.090→0.275 | 0.00 / 0.000 | 0.000 | 490.212 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.818
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.818
- phase_score: 0.187
- phase_breakdown.insert_score: 0.369
- phase_breakdown.approach_score: 0.005
- phase_breakdown.contact_score: 0.007
- phase_breakdown.align_score: 0.004

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.440
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.864
- **Median Q (composite search score)**: 0.402
- **K-run variance**: 0.0004
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.431


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":84.0,"average_failure_rate":0.54194,"average_mean_iterations":113.08387,"average_solve_count":155.0,"average_success_count":71.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_align.arc_height":0.15672,"contact_probe.contact_force":8.96682,"insert_peg.insert_speed":0.02393,"insert_peg.insert_tolerance":0.01112},"optimized_scores":{"best_composite_score":0.42966,"best_fitness_score":0.43966,"best_task_score":0.81842},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link6","contact_count":280.0,"contact_point_centroid":[0.54606,0.02499,0.07919],"force_p95":896.19515,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1120.16854,"mean_force":320.4562,"phase_index":0.0,"phase_name":"approach_align","phase_type":"approach","tcp_position_centroid":[0.45037,0.02442,0.18509]},{"body_a":"peg_socket","body_b":"link7","contact_count":406.0,"contact_point_centroid":[0.54465,0.02546,0.07968],"force_p95":691.35318,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1109.75725,"mean_force":285.42981,"phase_index":0.0,"phase_name":"approach_align","phase_type":"approach","tcp_position_centroid":[0.4464,0.02241,0.17296]},{"body_a":"attachment","body_b":"peg_socket","contact_count":12.0,"contact_point_centroid":[0.44581,0.01233,0.07846],"force_p95":429.53104,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":954.51342,"mean_force":79.54278,"phase_index":0.0,"phase_name":"approach_align","phase_type":"approach","tcp_position_centroid":[0.44169,0.01228,0.09134]},{"body_a":"world","body_b":"link6","contact_count":52.0,"contact_point_centroid":[0.69654,0.04088,-0.00013],"force_p95":524.34539,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":586.4766,"mean_force":346.06829,"phase_index":1.0,"phase_name":"approach_descend","phase_type":"approach","tcp_position_centroid":[0.49371,0.03836,0.15901]},{"body_a":"peg_socket","body_b":"link7","contact_count":397.0,"contact_point_centroid":[0.54608,0.037,0.07993],"force_p95":345.74199,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":500.68987,"mean_force":238.46246,"phase_index":1.0,"phase_name":"approach_descend","phase_type":"approach","tcp_position_centroid":[0.47707,0.03166,0.184]},{"body_a":"peg_socket","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.54614,0.03503,0.08],"force_p95":282.78613,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":314.20681,"mean_force":104.7356,"phase_index":1.0,"phase_name":"approach_descend","phase_type":"approach","tcp_position_centroid":[0.45949,0.02567,0.19291]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.70359,0.03694,-1e-05],"force_p95":273.15114,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":273.15114,"mean_force":273.15114,"phase_index":2.0,"phase_name":"contact_probe","phase_type":"contact","tcp_position_centroid":[0.49686,0.0374,0.15937]},{"body_a":"world","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.70375,0.03808,-1e-05],"force_p95":119.64573,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":123.40354,"mean_force":85.82544,"phase_index":3.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.49708,0.03772,0.15946]},{"body_a":"attachment","body_b":"peg_socket","contact_count":7.0,"contact_point_centroid":[0.45629,0.00888,0.0796],"force_p95":0.0,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_align","phase_type":"approach","tcp_position_centroid":[0.44356,0.01219,0.09051]}],"total_contact_groups":9},"final_pose_error":0.35501,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.53301,0.0361,0.37689],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"peak_contact_force":1120.16854,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.49232,0.02716,0.17014],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.09446,"object_to_goal_dist_start":0.26034,"object_z_max":0.3442,"peak_contact_force":259.41975,"phase_name":"approach_align","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":705.0,"raw_peak_contact_force":1120.16854,"subtask_id":"align","tcp_end":[0.45949,0.02566,0.19294],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.53149,0.03882,0.13941],"object_pos_start":[0.49232,0.02716,0.17014],"object_to_goal_dist_end":0.07764,"object_to_goal_dist_start":0.09446,"object_z_max":0.17082,"peak_contact_force":210.33673,"phase_name":"approach_descend","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":452.0,"raw_peak_contact_force":586.4766,"subtask_id":"approach","tcp_end":[0.49686,0.0374,0.15937],"tcp_start":[0.45949,0.02566,0.19294],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.5316,0.03882,0.13952],"object_pos_start":[0.53149,0.03882,0.13941],"object_to_goal_dist_end":0.07777,"object_to_goal_dist_start":0.07764,"object_z_max":0.13941,"peak_contact_force":273.15114,"phase_name":"contact_probe","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":273.15114,"subtask_id":"contact","tcp_end":[0.49697,0.03741,0.15949],"tcp_start":[0.49686,0.0374,0.15937],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":610.0,"n_steps_budget":1000.0,"object_pos_end":[0.57298,0.0369,0.37537],"object_pos_start":[0.5316,0.03882,0.13952],"object_to_goal_dist_end":0.30648,"object_to_goal_dist_start":0.07777,"object_z_max":0.37435,"peak_contact_force":0.0,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":2.0,"raw_peak_contact_force":123.40354,"subtask_id":"insert","tcp_end":[0.53301,0.0361,0.37689],"tcp_start":[0.49697,0.03741,0.15949],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":109.0,"average_failure_rate":0.67702,"average_mean_iterations":138.78261,"average_solve_count":161.0,"average_success_count":52.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_align.arc_height":0.16762,"contact_probe.contact_force":14.00475,"insert_peg.insert_speed":0.02468,"insert_peg.insert_tolerance":0.00994},"optimized_scores":{"best_composite_score":0.38057,"best_fitness_score":0.39057,"best_task_score":0.86346},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":7.0,"contact_point_centroid":[0.47054,-0.00574,0.0795],"force_p95":1027.61858,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1057.6413,"mean_force":382.7425,"phase_index":0.0,"phase_name":"approach_align","phase_type":"approach","tcp_position_centroid":[0.4619,-0.00572,0.09195]},{"body_a":"peg_socket","body_b":"link7","contact_count":42.0,"contact_point_centroid":[0.5681,-0.00727,0.0789],"force_p95":692.38414,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":865.5252,"mean_force":233.40136,"phase_index":0.0,"phase_name":"approach_align","phase_type":"approach","tcp_position_centroid":[0.45395,-0.00681,0.11398]},{"body_a":"world","body_b":"link5","contact_count":50.0,"contact_point_centroid":[0.66011,0.09235,-0.00039],"force_p95":700.38669,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":851.11866,"mean_force":382.21678,"phase_index":3.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.50238,-0.01442,0.17158]},{"body_a":"peg_socket","body_b":"link6","contact_count":384.0,"contact_point_centroid":[0.58958,-0.01239,0.07983],"force_p95":279.8019,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":495.72781,"mean_force":246.85257,"phase_index":0.0,"phase_name":"approach_align","phase_type":"approach","tcp_position_centroid":[0.45797,-0.0098,0.16098]},{"body_a":"peg_socket","body_b":"link7","contact_count":175.0,"contact_point_centroid":[0.58959,-0.01559,0.07993],"force_p95":263.57023,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":310.79619,"mean_force":209.85687,"phase_index":3.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.49703,-0.01657,0.16848]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.58958,-0.01043,0.07991],"force_p95":282.87747,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":282.87747,"mean_force":282.87747,"phase_index":2.0,"phase_name":"contact_probe","phase_type":"contact","tcp_position_centroid":[0.49289,-0.01383,0.17142]},{"body_a":"peg_socket","body_b":"link6","contact_count":138.0,"contact_point_centroid":[0.58959,-0.01494,0.07993],"force_p95":216.08692,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":277.07238,"mean_force":150.69833,"phase_index":1.0,"phase_name":"approach_descend","phase_type":"approach","tcp_position_centroid":[0.47386,-0.01319,0.17766]},{"body_a":"peg_socket","body_b":"link7","contact_count":45.0,"contact_point_centroid":[0.58956,-0.00936,0.07988],"force_p95":206.73376,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":232.04665,"mean_force":171.27905,"phase_index":1.0,"phase_name":"approach_descend","phase_type":"approach","tcp_position_centroid":[0.4888,-0.01373,0.17386]},{"body_a":"peg_socket","body_b":"link7","contact_count":14.0,"contact_point_centroid":[0.55104,0.01325,0.07943],"force_p95":0.0,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_align","phase_type":"approach","tcp_position_centroid":[0.45474,-0.00619,0.09824]},{"body_a":"peg_socket","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.55149,-0.04707,0.07991],"force_p95":0.0,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_align","phase_type":"approach","tcp_position_centroid":[0.45438,-0.00614,0.09678]}],"total_contact_groups":10},"final_pose_error":0.27914,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.5298,-0.02034,0.30412],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":1057.6413,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.49905,-0.01262,0.16244],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.08341,"object_to_goal_dist_start":0.26034,"object_z_max":0.34486,"peak_contact_force":281.48885,"phase_name":"approach_align","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":451.0,"raw_peak_contact_force":1057.6413,"subtask_id":"align","tcp_end":[0.46183,-0.01277,0.1771],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":213.0,"n_steps_budget":600.0,"object_pos_end":[0.52936,-0.01374,0.155],"object_pos_start":[0.49905,-0.01262,0.16244],"object_to_goal_dist_end":0.08171,"object_to_goal_dist_start":0.08341,"object_z_max":0.16312,"peak_contact_force":175.17906,"phase_name":"approach_descend","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":183.0,"raw_peak_contact_force":277.07238,"subtask_id":"approach","tcp_end":[0.49289,-0.01383,0.17142],"tcp_start":[0.46183,-0.01277,0.1771],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":690.0,"object_pos_end":[0.52943,-0.01378,0.15501],"object_pos_start":[0.52936,-0.01374,0.155],"object_to_goal_dist_end":0.08174,"object_to_goal_dist_start":0.08171,"object_z_max":0.155,"peak_contact_force":282.87747,"phase_name":"contact_probe","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":282.87747,"subtask_id":"contact","tcp_end":[0.49295,-0.01387,0.17142],"tcp_start":[0.49289,-0.01383,0.17142],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":369.0,"n_steps_budget":1000.0,"object_pos_end":[0.56955,-0.02047,0.29963],"object_pos_start":[0.52943,-0.01378,0.15501],"object_to_goal_dist_end":0.23128,"object_to_goal_dist_start":0.08174,"object_z_max":0.29784,"peak_contact_force":0.0,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":225.0,"raw_peak_contact_force":851.11866,"subtask_id":"insert","tcp_end":[0.5298,-0.02034,0.30412],"tcp_start":[0.49295,-0.01387,0.17142],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":121.0,"average_failure_rate":0.74233,"average_mean_iterations":152.14724,"average_solve_count":163.0,"average_success_count":42.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_align.arc_height":0.14622,"contact_probe.contact_force":14.25128,"insert_peg.insert_speed":0.01692,"insert_peg.insert_tolerance":0.00669},"optimized_scores":{"best_composite_score":0.40184,"best_fitness_score":0.41184,"best_task_score":0.86402},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":34.0,"contact_point_centroid":[0.56677,-0.00946,0.07823],"force_p95":569.52033,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1115.65761,"mean_force":140.88979,"phase_index":0.0,"phase_name":"approach_align","phase_type":"approach","tcp_position_centroid":[0.45323,-0.00833,0.10477]},{"body_a":"peg_socket","body_b":"link7","contact_count":30.0,"contact_point_centroid":[0.59634,-0.02141,0.07988],"force_p95":497.31048,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":986.89063,"mean_force":322.35342,"phase_index":1.0,"phase_name":"approach_descend","phase_type":"approach","tcp_position_centroid":[0.494,-0.02065,0.17544]},{"body_a":"peg_socket","body_b":"link6","contact_count":134.0,"contact_point_centroid":[0.59646,-0.01998,0.07994],"force_p95":210.91126,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":960.60807,"mean_force":166.13346,"phase_index":1.0,"phase_name":"approach_descend","phase_type":"approach","tcp_position_centroid":[0.48018,-0.01895,0.18194]},{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.47652,-0.00763,0.07988],"force_p95":670.22109,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":788.49539,"mean_force":197.12385,"phase_index":0.0,"phase_name":"approach_align","phase_type":"approach","tcp_position_centroid":[0.46053,-0.00756,0.09037]},{"body_a":"peg_socket","body_b":"link7","contact_count":26.0,"contact_point_centroid":[0.54808,0.0073,0.07808],"force_p95":299.57469,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":708.60224,"mean_force":77.14581,"phase_index":0.0,"phase_name":"approach_align","phase_type":"approach","tcp_position_centroid":[0.45268,-0.00828,0.10129]},{"body_a":"peg_socket","body_b":"link5","contact_count":1.0,"contact_point_centroid":[0.59634,0.03587,0.07977],"force_p95":519.38365,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":519.38365,"mean_force":519.38365,"phase_index":2.0,"phase_name":"contact_probe","phase_type":"contact","tcp_position_centroid":[0.50054,-0.04884,0.18239]},{"body_a":"peg_socket","body_b":"link5","contact_count":54.0,"contact_point_centroid":[0.59617,0.0345,0.07957],"force_p95":431.00565,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":496.11461,"mean_force":195.16482,"phase_index":3.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.50411,-0.04354,0.19085]},{"body_a":"peg_socket","body_b":"link6","contact_count":404.0,"contact_point_centroid":[0.59609,-0.01665,0.07981],"force_p95":278.28176,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":326.39352,"mean_force":243.82912,"phase_index":0.0,"phase_name":"approach_align","phase_type":"approach","tcp_position_centroid":[0.45898,-0.01357,0.15806]},{"body_a":"peg_socket","body_b":"link7","contact_count":14.0,"contact_point_centroid":[0.54868,-0.05354,0.07912],"force_p95":0.0,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_align","phase_type":"approach","tcp_position_centroid":[0.45214,-0.0082,0.09618]}],"total_contact_groups":9},"final_pose_error":0.33014,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53648,-0.02339,0.025],"final_tcp_position":[0.52454,-0.06106,0.35277],"realised_fixture_position":[0.53648,-0.02339,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53648,-0.02339,0.08]},"peak_contact_force":1115.65761,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.50394,-0.01826,0.16781],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.08977,"object_to_goal_dist_start":0.26034,"object_z_max":0.34494,"peak_contact_force":249.28374,"phase_name":"approach_align","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":482.0,"raw_peak_contact_force":1115.65761,"subtask_id":"align","tcp_end":[0.46723,-0.01852,0.18369],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":213.0,"n_steps_budget":600.0,"object_pos_end":[0.53341,-0.03147,0.15515],"object_pos_start":[0.50394,-0.01826,0.16781],"object_to_goal_dist_end":0.08806,"object_to_goal_dist_start":0.08977,"object_z_max":0.16781,"peak_contact_force":0.0,"phase_name":"approach_descend","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":164.0,"raw_peak_contact_force":986.89063,"subtask_id":"approach","tcp_end":[0.49653,-0.02891,0.17042],"tcp_start":[0.46723,-0.01852,0.18369],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":22.0,"n_steps_budget":690.0,"object_pos_end":[0.53821,-0.05372,0.16974],"object_pos_start":[0.53341,-0.03147,0.15515],"object_to_goal_dist_end":0.11135,"object_to_goal_dist_start":0.08806,"object_z_max":0.16864,"peak_contact_force":519.38365,"phase_name":"contact_probe","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":519.38365,"subtask_id":"contact","tcp_end":[0.50084,-0.04958,0.1834],"tcp_start":[0.49653,-0.02891,0.17042],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":154.0,"n_steps_budget":1000.0,"object_pos_end":[0.56426,-0.06574,0.35286],"object_pos_start":[0.53821,-0.05372,0.16974],"object_to_goal_dist_end":0.28793,"object_to_goal_dist_start":0.11135,"object_z_max":0.35131,"peak_contact_force":0.0,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":54.0,"raw_peak_contact_force":496.11461,"subtask_id":"insert","tcp_end":[0.52454,-0.06106,0.35277],"tcp_start":[0.50084,-0.04958,0.1834],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```