## Search State

- **Seed**: 8
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → approach → contact → insert | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | 3 | 0.3783 | 0.84 | ❌ rejected |
| 0 | approach → approach → contact → insert | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | 3 | 0.4827 | 0.86 | ✅ accepted |

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

## Current Skill (Q=0.378) — your mutation base

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

- **Composite score**: 0.378
- **task_score** (E): 0.836
- **fitness_score**: 0.338  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_lateral | 0.00 | 1.00 | 0.1572 |
| approach_descend | 0.67 | 0.67 | 0.0466 |
| contact_1 | 1.00 | 1.00 | 0.0001 |
| insert_1 | 0.00 | 0.67 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_lateral | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.446, -0.005, 0.154) | (0.504, -0.000, 0.340)→(0.485, -0.004, 0.145) | 0.260→0.070 | 1.00 / 1.333 | 220.564 | 1065.130 |
| approach_descend | approach | 0.67 / step_budget | (0.446, -0.005, 0.154)→(0.491, 0.000, 0.156) | (0.485, -0.004, 0.145)→(0.528, 0.001, 0.143) | 0.070→0.074 | 0.67 / 0.667 | 84.508 | 325.698 |
| contact_1 | contact | 1.00 / force_exceeded | (0.491, 0.000, 0.156)→(0.491, 0.000, 0.156) | (0.528, 0.001, 0.143)→(0.528, 0.001, 0.143) | 0.074→0.074 | 1.00 / 1.000 | 252.686 | 252.686 |
| insert_1 | insert | 0.00 / guard_failure | (0.491, 0.000, 0.156)→(0.491, 0.000, 0.156) | (0.528, 0.001, 0.143)→(0.528, 0.001, 0.143) | 0.074→0.074 | 0.67 / 0.667 | 74.391 | 299.846 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.855
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.855
- phase_score: 0.005
- phase_breakdown.insert_score: 0.007
- phase_breakdown.approach_score: 0.004
- phase_breakdown.contact_score: 0.006
- phase_breakdown.align_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.345
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.855
- **Median Q (composite search score)**: 0.385
- **K-run variance**: 0.0001
- **Stagnated**: yes
  → Parameter optimiser converged to local optimum; structural change likely needed
- **Stop reason**: tolfun
- **Mean generations**: 2.0
- **Final σ (mean)**: 0.263


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.5,"average_solve_count":44.0,"average_success_count":44.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":11.13629,"insert_1.insert_speed":0.02468,"insert_1.insertion_distance":0.04051},"optimized_scores":{"best_composite_score":0.36499,"best_fitness_score":0.32499,"best_task_score":0.80189},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":341.0,"contact_point_centroid":[0.5435,0.02009,0.07963],"force_p95":360.68645,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1050.7215,"mean_force":233.0256,"phase_index":0.0,"phase_name":"approach_lateral","phase_type":"approach","tcp_position_centroid":[0.43122,0.01633,0.15675]},{"body_a":"peg_socket","body_b":"link6","contact_count":287.0,"contact_point_centroid":[0.54611,0.01916,0.07941],"force_p95":316.61599,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":446.74336,"mean_force":207.65817,"phase_index":0.0,"phase_name":"approach_lateral","phase_type":"approach","tcp_position_centroid":[0.43141,0.01714,0.1644]},{"body_a":"peg_socket","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.54614,0.04178,0.07997],"force_p95":339.42146,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":346.73907,"mean_force":273.56298,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.48404,0.03542,0.16391]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54612,0.04178,0.07994],"force_p95":343.2964,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":343.2964,"mean_force":343.2964,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.484,0.03543,0.16389]},{"body_a":"peg_socket","body_b":"link7","contact_count":469.0,"contact_point_centroid":[0.54611,0.03234,0.07994],"force_p95":191.91495,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":277.42744,"mean_force":134.79433,"phase_index":1.0,"phase_name":"approach_descend","phase_type":"approach","tcp_position_centroid":[0.45813,0.02481,0.16885]},{"body_a":"peg_socket","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.54613,0.02235,0.07999],"force_p95":54.38419,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":60.42687,"mean_force":20.14229,"phase_index":1.0,"phase_name":"approach_descend","phase_type":"approach","tcp_position_centroid":[0.43193,0.01504,0.16519]},{"body_a":"attachment","body_b":"peg_socket","contact_count":8.0,"contact_point_centroid":[0.43819,0.01085,0.07946],"force_p95":0.0,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_lateral","phase_type":"approach","tcp_position_centroid":[0.43432,0.01078,0.09341]}],"total_contact_groups":7},"final_pose_error":0.04063,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.48411,0.03541,0.16401],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"peak_contact_force":1050.7215,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.4697,0.01747,0.15227],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.08029,"object_to_goal_dist_start":0.26034,"object_z_max":0.344,"peak_contact_force":179.34222,"phase_name":"approach_lateral","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":636.0,"raw_peak_contact_force":1050.7215,"tcp_end":[0.43192,0.01505,0.16519],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.51904,0.03729,0.1447],"object_pos_start":[0.4697,0.01747,0.15227],"object_to_goal_dist_end":0.07707,"object_to_goal_dist_start":0.08029,"object_z_max":0.15523,"peak_contact_force":140.87573,"phase_name":"approach_descend","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":472.0,"raw_peak_contact_force":277.42744,"tcp_end":[0.484,0.03543,0.16389],"tcp_start":[0.43192,0.01505,0.16519],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.51907,0.03727,0.1447],"object_pos_start":[0.51904,0.03729,0.1447],"object_to_goal_dist_end":0.07707,"object_to_goal_dist_start":0.07707,"object_z_max":0.1447,"peak_contact_force":343.2964,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":343.2964,"tcp_end":[0.48402,0.03542,0.16389],"tcp_start":[0.484,0.03543,0.16389],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.51911,0.03728,0.14475],"object_pos_start":[0.51907,0.03727,0.1447],"object_to_goal_dist_end":0.07712,"object_to_goal_dist_start":0.07707,"object_z_max":0.14482,"peak_contact_force":0.0,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":2.0,"raw_peak_contact_force":346.73907,"tcp_end":[0.48411,0.03541,0.16401],"tcp_start":[0.48409,0.0354,0.16398],"tcp_to_object_dist_end":0.03999,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":6.0,"average_failure_rate":0.13636,"average_mean_iterations":32.36364,"average_solve_count":44.0,"average_success_count":38.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":15.07478,"insert_1.insert_speed":0.03114,"insert_1.insertion_distance":0.03786},"optimized_scores":{"best_composite_score":0.38523,"best_fitness_score":0.34523,"best_task_score":0.85482},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":31.0,"contact_point_centroid":[0.56002,-0.01284,0.07813],"force_p95":978.42121,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1065.73346,"mean_force":334.4333,"phase_index":0.0,"phase_name":"approach_lateral","phase_type":"approach","tcp_position_centroid":[0.45296,-0.01059,0.10534]},{"body_a":"peg_socket","body_b":"link6","contact_count":67.0,"contact_point_centroid":[0.58961,-0.01623,0.07995],"force_p95":212.35331,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":350.50239,"mean_force":133.52853,"phase_index":1.0,"phase_name":"approach_descend","phase_type":"approach","tcp_position_centroid":[0.46084,-0.01371,0.14813]},{"body_a":"peg_socket","body_b":"link6","contact_count":134.0,"contact_point_centroid":[0.58957,-0.0155,0.07989],"force_p95":275.73782,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":293.31637,"mean_force":244.35188,"phase_index":0.0,"phase_name":"approach_lateral","phase_type":"approach","tcp_position_centroid":[0.45638,-0.01255,0.14285]},{"body_a":"peg_socket","body_b":"link7","contact_count":208.0,"contact_point_centroid":[0.5896,-0.01328,0.07992],"force_p95":159.45317,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":292.14248,"mean_force":120.77744,"phase_index":1.0,"phase_name":"approach_descend","phase_type":"approach","tcp_position_centroid":[0.48115,-0.01451,0.15085]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.58961,-0.01685,0.07995],"force_p95":262.92486,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":262.92486,"mean_force":262.92486,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49755,-0.01525,0.14858]},{"body_a":"peg_socket","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.58961,-0.0169,0.07995],"force_p95":243.06089,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":261.69726,"mean_force":128.58568,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49762,-0.01526,0.14849]},{"body_a":"peg_socket","body_b":"link7","contact_count":15.0,"contact_point_centroid":[0.54888,-0.04721,0.07911],"force_p95":93.29629,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":185.57854,"mean_force":15.95502,"phase_index":0.0,"phase_name":"approach_lateral","phase_type":"approach","tcp_position_centroid":[0.45248,-0.01029,0.09886]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.46963,-0.00988,0.07995],"force_p95":0.0,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_lateral","phase_type":"approach","tcp_position_centroid":[0.46039,-0.00988,0.09276]},{"body_a":"peg_socket","body_b":"link7","contact_count":11.0,"contact_point_centroid":[0.54825,0.01326,0.07957],"force_p95":0.0,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_lateral","phase_type":"approach","tcp_position_centroid":[0.45243,-0.01024,0.09756]}],"total_contact_groups":9},"final_pose_error":0.03786,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.49763,-0.01527,0.14852],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":1065.73346,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":255.0,"n_steps_budget":600.0,"object_pos_end":[0.49385,-0.01373,0.13964],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.0615,"object_to_goal_dist_start":0.26034,"object_z_max":0.34537,"peak_contact_force":225.75434,"phase_name":"approach_lateral","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":192.0,"raw_peak_contact_force":1065.73346,"tcp_end":[0.45434,-0.01346,0.14587],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":316.0,"n_steps_budget":600.0,"object_pos_end":[0.53631,-0.01557,0.13871],"object_pos_start":[0.49385,-0.01373,0.13964],"object_to_goal_dist_end":0.07077,"object_to_goal_dist_start":0.0615,"object_z_max":0.14291,"peak_contact_force":112.64778,"phase_name":"approach_descend","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":275.0,"raw_peak_contact_force":350.50239,"tcp_end":[0.49755,-0.01525,0.14858],"tcp_start":[0.45434,-0.01346,0.14587],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.53637,-0.01557,0.13867],"object_pos_start":[0.53631,-0.01557,0.13871],"object_to_goal_dist_end":0.07076,"object_to_goal_dist_start":0.07077,"object_z_max":0.13871,"peak_contact_force":262.92486,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":262.92486,"tcp_end":[0.49761,-0.01525,0.14852],"tcp_start":[0.49755,-0.01525,0.14858],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":780.0,"object_pos_end":[0.5364,-0.01559,0.13863],"object_pos_start":[0.53637,-0.01557,0.13867],"object_to_goal_dist_end":0.07074,"object_to_goal_dist_start":0.07076,"object_z_max":0.13867,"peak_contact_force":48.72622,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":261.69726,"tcp_end":[0.49763,-0.01527,0.14852],"tcp_start":[0.49763,-0.01527,0.14849],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":8.0,"average_failure_rate":0.17778,"average_mean_iterations":40.48889,"average_solve_count":45.0,"average_success_count":37.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":14.8508,"insert_1.insert_speed":0.02557,"insert_1.insertion_distance":0.04619},"optimized_scores":{"best_composite_score":0.38454,"best_fitness_score":0.34454,"best_task_score":0.8518},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":38.0,"contact_point_centroid":[0.56836,-0.01195,0.07798],"force_p95":733.29683,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1078.93508,"mean_force":123.81515,"phase_index":0.0,"phase_name":"approach_lateral","phase_type":"approach","tcp_position_centroid":[0.45059,-0.01148,0.10729]},{"body_a":"peg_socket","body_b":"link6","contact_count":239.0,"contact_point_centroid":[0.59543,-0.01724,0.07972],"force_p95":273.91722,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":446.89667,"mean_force":234.90675,"phase_index":0.0,"phase_name":"approach_lateral","phase_type":"approach","tcp_position_centroid":[0.45239,-0.01388,0.1386]},{"body_a":"peg_socket","body_b":"link6","contact_count":165.0,"contact_point_centroid":[0.59647,-0.02053,0.07994],"force_p95":223.5346,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":349.16527,"mean_force":136.53322,"phase_index":1.0,"phase_name":"approach_descend","phase_type":"approach","tcp_position_centroid":[0.46488,-0.01764,0.1583]},{"body_a":"peg_socket","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.59646,-0.01804,0.07992],"force_p95":288.46601,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":291.10281,"mean_force":243.4278,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49152,-0.01941,0.1564]},{"body_a":"peg_socket","body_b":"link7","contact_count":70.0,"contact_point_centroid":[0.59644,-0.01643,0.07989],"force_p95":172.88536,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":249.43723,"mean_force":131.62728,"phase_index":1.0,"phase_name":"approach_descend","phase_type":"approach","tcp_position_centroid":[0.48522,-0.01902,0.15804]},{"body_a":"peg_socket","body_b":"link7","contact_count":24.0,"contact_point_centroid":[0.54497,0.00759,0.07816],"force_p95":189.22079,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":191.3539,"mean_force":79.28714,"phase_index":0.0,"phase_name":"approach_lateral","phase_type":"approach","tcp_position_centroid":[0.44995,-0.01128,0.1008]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.59646,-0.01798,0.07994],"force_p95":151.8376,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":151.8376,"mean_force":151.8376,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49137,-0.01941,0.15661]},{"body_a":"peg_socket","body_b":"link7","contact_count":18.0,"contact_point_centroid":[0.54556,-0.05365,0.07849],"force_p95":0.0,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_lateral","phase_type":"approach","tcp_position_centroid":[0.44969,-0.01119,0.09832]}],"total_contact_groups":8},"final_pose_error":0.04596,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53648,-0.02339,0.025],"final_tcp_position":[0.49164,-0.01942,0.15628],"realised_fixture_position":[0.53648,-0.02339,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53648,-0.02339,0.08]},"peak_contact_force":1078.93508,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":343.0,"n_steps_budget":600.0,"object_pos_end":[0.49058,-0.01693,0.14411],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.06697,"object_to_goal_dist_start":0.26034,"object_z_max":0.34522,"peak_contact_force":256.59684,"phase_name":"approach_lateral","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":319.0,"raw_peak_contact_force":1078.93508,"tcp_end":[0.45126,-0.01674,0.15145],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":273.0,"n_steps_budget":600.0,"object_pos_end":[0.52979,-0.01966,0.14536],"object_pos_start":[0.49058,-0.01693,0.14411],"object_to_goal_dist_end":0.07447,"object_to_goal_dist_start":0.06697,"object_z_max":0.15033,"peak_contact_force":0.0,"phase_name":"approach_descend","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":235.0,"raw_peak_contact_force":349.16527,"tcp_end":[0.49142,-0.01941,0.15665],"tcp_start":[0.45126,-0.01674,0.15145],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":2.0,"n_steps_budget":630.0,"object_pos_end":[0.52984,-0.01966,0.1452],"object_pos_start":[0.52979,-0.01966,0.14536],"object_to_goal_dist_end":0.07435,"object_to_goal_dist_start":0.07447,"object_z_max":0.14536,"peak_contact_force":151.8376,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":151.8376,"tcp_end":[0.49147,-0.01941,0.15651],"tcp_start":[0.49142,-0.01941,0.15665],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.52989,-0.01966,0.1451],"object_pos_start":[0.52984,-0.01966,0.1452],"object_to_goal_dist_end":0.07429,"object_to_goal_dist_start":0.07435,"object_z_max":0.1452,"peak_contact_force":174.44579,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":291.10281,"tcp_end":[0.49164,-0.01942,0.15628],"tcp_start":[0.49158,-0.01942,0.15631],"tcp_to_object_dist_end":0.03986,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```