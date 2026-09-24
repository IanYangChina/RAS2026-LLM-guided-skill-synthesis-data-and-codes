## Search State

- **Seed**: 8
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → align → contact → insert | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 3 | 0.3112 | 0.86 | ❌ rejected |
| 13 | approach → align → contact → insert → retract | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | time_limit | 8 | 0.1049 | 0.85 | ❌ rejected |
| 12 | approach → approach → contact → insert | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | 3 | 0.4813 | 0.86 | ❌ rejected |
| 11 | approach → approach → contact → insert | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | 3 | 0.4818 | 0.86 | ❌ rejected |
| 10 | approach → align → contact → insert | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8 | 0.1481 | 0.84 | ❌ rejected |

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

## Current Skill (Q=0.311) — your mutation base

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

- **Composite score**: 0.311
- **task_score** (E): 0.856
- **fitness_score**: 0.355  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 0.00 | 1.00 | 0.1286 |
| descend | 0.33 | 0.67 | 0.0477 |
| contact | 0.67 | 0.67 | 0.0087 |
| insert | 0.00 | 0.33 | 0.0002 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.472, -0.009, 0.176) | (0.504, -0.000, 0.340)→(0.509, -0.007, 0.160) | 0.260→0.082 | 1.00 / 1.000 | 272.324 | 1617.258 |
| descend | align | 0.33 / step_budget | (0.472, -0.009, 0.176)→(0.507, -0.001, 0.183) | (0.509, -0.007, 0.160)→(0.545, 0.002, 0.172) | 0.082→0.110 | 0.67 / 0.667 | 102.116 | 731.621 |
| contact | contact | 0.67 / force_exceeded | (0.507, -0.001, 0.183)→(0.508, 0.000, 0.191) | (0.545, 0.002, 0.172)→(0.547, 0.003, 0.182) | 0.110→0.119 | 0.67 / 0.667 | 66.954 | 106.068 |
| insert | insert | 0.00 / guard_failure | (0.508, 0.000, 0.191)→(0.508, 0.000, 0.191) | (0.547, 0.003, 0.182)→(0.547, 0.003, 0.182) | 0.119→0.119 | 0.33 / 0.333 | 75.674 | 152.132 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.867
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.867
- phase_score: 0.021
- phase_breakdown.insert_score: 0.027
- phase_breakdown.approach_score: 0.010
- phase_breakdown.contact_score: 0.022
- phase_breakdown.align_score: 0.007

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.368
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.867
- **Median Q (composite search score)**: 0.376
- **K-run variance**: 0.0118
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.3
- **Final σ (mean)**: 0.261


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.1,"average_solve_count":50.0,"average_success_count":50.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact.contact_force":10.0094,"insert.insert_speed":0.0164,"insert.insertion_distance":0.09753},"optimized_scores":{"best_composite_score":0.37594,"best_fitness_score":0.33594,"best_task_score":0.83598},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":10.0,"contact_point_centroid":[0.45103,0.00568,0.07887],"force_p95":1596.41342,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2902.56985,"mean_force":290.25698,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.44694,0.00485,0.09193]},{"body_a":"attachment","body_b":"peg_socket","contact_count":11.0,"contact_point_centroid":[0.45731,0.00481,0.07927],"force_p95":1768.51353,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2480.83259,"mean_force":489.43788,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.44918,0.00484,0.09175]},{"body_a":"peg_socket","body_b":"link7","contact_count":540.0,"contact_point_centroid":[0.54597,0.01091,0.07984],"force_p95":293.51313,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":693.5192,"mean_force":284.64677,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.46571,0.00414,0.12995]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.54616,0.04014,0.08],"force_p95":272.62948,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":272.62948,"mean_force":272.62948,"phase_index":2.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.48064,0.03093,0.1067]},{"body_a":"attachment","body_b":"peg_socket","contact_count":2.0,"contact_point_centroid":[0.54616,0.0402,0.07999],"force_p95":224.79009,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":229.37368,"mean_force":183.53784,"phase_index":3.0,"phase_name":"insert","phase_type":"insert","tcp_position_centroid":[0.48069,0.03098,0.10666]},{"body_a":"attachment","body_b":"peg_socket","contact_count":19.0,"contact_point_centroid":[0.54614,0.03946,0.07988],"force_p95":111.31306,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":119.93245,"mean_force":95.38161,"phase_index":1.0,"phase_name":"descend","phase_type":"align","tcp_position_centroid":[0.47963,0.03,0.10654]},{"body_a":"peg_socket","body_b":"link7","contact_count":65.0,"contact_point_centroid":[0.54614,0.02219,0.07999],"force_p95":98.69503,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":106.96957,"mean_force":69.5955,"phase_index":1.0,"phase_name":"descend","phase_type":"align","tcp_position_centroid":[0.47051,0.00682,0.12715]}],"total_contact_groups":7},"final_pose_error":0.09755,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.48074,0.03099,0.10667],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"peak_contact_force":2902.56985,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":632.0,"n_steps_budget":690.0,"object_pos_end":[0.50675,0.00686,0.12606],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.04706,"object_to_goal_dist_start":0.26034,"object_z_max":0.34436,"peak_contact_force":278.11235,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":561.0,"raw_peak_contact_force":2902.56985,"tcp_end":[0.46761,0.00145,0.13228],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":210.0,"n_steps_budget":600.0,"object_pos_end":[0.51969,0.03624,0.09986],"object_pos_start":[0.50675,0.00686,0.12606],"object_to_goal_dist_end":0.04578,"object_to_goal_dist_start":0.04706,"object_z_max":0.12608,"peak_contact_force":98.00104,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":84.0,"raw_peak_contact_force":119.93245,"tcp_end":[0.48064,0.03093,0.1067],"tcp_start":[0.46761,0.00145,0.13228],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":4.0,"n_steps_budget":600.0,"object_pos_end":[0.51973,0.0363,0.09983],"object_pos_start":[0.51969,0.03624,0.09986],"object_to_goal_dist_end":0.04583,"object_to_goal_dist_start":0.04578,"object_z_max":0.09991,"peak_contact_force":155.28588,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":272.62948,"tcp_end":[0.48068,0.03098,0.10666],"tcp_start":[0.48064,0.03093,0.1067],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.51976,0.03631,0.09984],"object_pos_start":[0.51973,0.0363,0.09983],"object_to_goal_dist_end":0.04585,"object_to_goal_dist_start":0.04583,"object_z_max":0.09986,"peak_contact_force":0.0,"phase_name":"insert","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":2.0,"raw_peak_contact_force":229.37368,"tcp_end":[0.48074,0.03099,0.10667],"tcp_start":[0.48073,0.03099,0.10668],"tcp_to_object_dist_end":0.03997,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":69.0,"average_failure_rate":0.61062,"average_mean_iterations":126.0354,"average_solve_count":113.0,"average_success_count":44.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact.contact_force":7.66306,"insert.insert_speed":0.02899,"insert.insertion_distance":0.0508},"optimized_scores":{"best_composite_score":0.15838,"best_fitness_score":0.36838,"best_task_score":0.86457},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link5","contact_count":14.0,"contact_point_centroid":[0.65261,0.09209,-0.0011],"force_p95":1368.90851,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1445.58938,"mean_force":819.17335,"phase_index":1.0,"phase_name":"descend","phase_type":"align","tcp_position_centroid":[0.50251,-0.01718,0.17727]},{"body_a":"attachment","body_b":"peg_socket","contact_count":6.0,"contact_point_centroid":[0.47042,-0.00294,0.07927],"force_p95":965.30188,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1004.5207,"mean_force":428.5552,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.46076,-0.00295,0.09104]},{"body_a":"peg_socket","body_b":"link7","contact_count":34.0,"contact_point_centroid":[0.56585,-0.00293,0.07926],"force_p95":723.06744,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":976.2517,"mean_force":226.78563,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.44718,-0.00367,0.11325]},{"body_a":"peg_socket","body_b":"link5","contact_count":16.0,"contact_point_centroid":[0.58829,0.04142,0.06611],"force_p95":741.10887,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":816.11254,"mean_force":460.86105,"phase_index":1.0,"phase_name":"descend","phase_type":"align","tcp_position_centroid":[0.51599,-0.01908,0.20799]},{"body_a":"peg_socket","body_b":"link7","contact_count":69.0,"contact_point_centroid":[0.58956,-0.01028,0.07995],"force_p95":462.96861,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":592.98056,"mean_force":295.35117,"phase_index":1.0,"phase_name":"descend","phase_type":"align","tcp_position_centroid":[0.49687,-0.0126,0.17946]},{"body_a":"peg_socket","body_b":"link6","contact_count":485.0,"contact_point_centroid":[0.58949,-0.00835,0.07983],"force_p95":290.61539,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":532.34856,"mean_force":248.97498,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.45718,-0.00589,0.17048]},{"body_a":"peg_socket","body_b":"link6","contact_count":148.0,"contact_point_centroid":[0.58957,-0.01226,0.07991],"force_p95":335.46436,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":396.46855,"mean_force":192.84805,"phase_index":1.0,"phase_name":"descend","phase_type":"align","tcp_position_centroid":[0.4836,-0.01081,0.19373]},{"body_a":"peg_socket","body_b":"link7","contact_count":13.0,"contact_point_centroid":[0.54668,0.01324,0.07917],"force_p95":115.20108,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":137.32365,"mean_force":27.27928,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.45002,-0.00339,0.09829]},{"body_a":"peg_socket","body_b":"link5","contact_count":8.0,"contact_point_centroid":[0.55953,0.04253,0.07991],"force_p95":0.0,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend","phase_type":"align","tcp_position_centroid":[0.51554,-0.02055,0.20697]}],"total_contact_groups":9},"final_pose_error":0.05033,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.52546,-0.00697,0.24943],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":1445.58938,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.50645,-0.01028,0.17819],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.09894,"object_to_goal_dist_start":0.26034,"object_z_max":0.34477,"peak_contact_force":267.48341,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":538.0,"raw_peak_contact_force":1004.5207,"tcp_end":[0.47175,-0.01057,0.19809],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":333.0,"n_steps_budget":690.0,"object_pos_end":[0.55938,-0.00699,0.21429],"object_pos_start":[0.50645,-0.01028,0.17819],"object_to_goal_dist_end":0.147,"object_to_goal_dist_start":0.09894,"object_z_max":0.21166,"peak_contact_force":0.0,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":255.0,"raw_peak_contact_force":1445.58938,"tcp_end":[0.5209,-0.00875,0.22509],"tcp_start":[0.47175,-0.01057,0.19809],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":31.0,"n_steps_budget":900.0,"object_pos_end":[0.56466,-0.00479,0.24178],"object_pos_start":[0.55938,-0.00699,0.21429],"object_to_goal_dist_end":0.17429,"object_to_goal_dist_start":0.147,"object_z_max":0.24171,"peak_contact_force":0.0,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.52555,-0.0069,0.2499],"tcp_start":[0.5209,-0.00875,0.22509],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":5.0,"n_steps_budget":1000.0,"object_pos_end":[0.56457,-0.00487,0.24129],"object_pos_start":[0.56466,-0.00479,0.24178],"object_to_goal_dist_end":0.17381,"object_to_goal_dist_start":0.17429,"object_z_max":0.24178,"peak_contact_force":0.0,"phase_name":"insert","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.52546,-0.00697,0.24943],"tcp_start":[0.52555,-0.0069,0.2499],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":11.0,"average_failure_rate":0.20755,"average_mean_iterations":47.39623,"average_solve_count":53.0,"average_success_count":42.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact.contact_force":10.05333,"insert.insert_speed":0.046,"insert.insertion_distance":0.09104},"optimized_scores":{"best_composite_score":0.39923,"best_fitness_score":0.35923,"best_task_score":0.8673},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":30.0,"contact_point_centroid":[0.54755,0.00727,0.07817],"force_p95":821.60751,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":944.68465,"mean_force":191.76686,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.45221,-0.00449,0.10364]},{"body_a":"attachment","body_b":"peg_socket","contact_count":2.0,"contact_point_centroid":[0.4765,-0.00393,0.07994],"force_p95":827.7109,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":828.98078,"mean_force":816.28196,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.46731,-0.00393,0.09235]},{"body_a":"world","body_b":"link5","contact_count":17.0,"contact_point_centroid":[0.65508,0.07585,-0.00093],"force_p95":618.49831,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":629.34202,"mean_force":501.57658,"phase_index":1.0,"phase_name":"descend","phase_type":"align","tcp_position_centroid":[0.50556,-0.02416,0.18301]},{"body_a":"peg_socket","body_b":"link5","contact_count":19.0,"contact_point_centroid":[0.59607,0.03556,0.06471],"force_p95":526.04386,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":572.52459,"mean_force":196.26471,"phase_index":1.0,"phase_name":"descend","phase_type":"align","tcp_position_centroid":[0.51708,-0.02484,0.21285]},{"body_a":"peg_socket","body_b":"link6","contact_count":132.0,"contact_point_centroid":[0.59644,-0.01615,0.07992],"force_p95":367.92023,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":440.18673,"mean_force":213.19733,"phase_index":1.0,"phase_name":"descend","phase_type":"align","tcp_position_centroid":[0.4883,-0.01657,0.19101]},{"body_a":"peg_socket","body_b":"link7","contact_count":42.0,"contact_point_centroid":[0.59639,-0.01166,0.0799],"force_p95":327.71745,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":359.7796,"mean_force":265.12132,"phase_index":1.0,"phase_name":"descend","phase_type":"align","tcp_position_centroid":[0.49888,-0.01612,0.1797]},{"body_a":"peg_socket","body_b":"link7","contact_count":38.0,"contact_point_centroid":[0.57036,-0.00434,0.07882],"force_p95":283.38979,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":334.1009,"mean_force":66.50889,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.45274,-0.00458,0.10895]},{"body_a":"peg_socket","body_b":"link6","contact_count":489.0,"contact_point_centroid":[0.59616,-0.01199,0.07981],"force_p95":289.38188,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":322.33317,"mean_force":246.40835,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.46231,-0.00941,0.16204]},{"body_a":"peg_socket","body_b":"link5","contact_count":5.0,"contact_point_centroid":[0.59634,0.03436,0.0726],"force_p95":189.35391,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":227.02105,"mean_force":53.14128,"phase_index":3.0,"phase_name":"insert","phase_type":"insert","tcp_position_centroid":[0.51835,-0.02391,0.21703]},{"body_a":"peg_socket","body_b":"link5","contact_count":2.0,"contact_point_centroid":[0.59631,0.03388,0.07067],"force_p95":43.29701,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":45.5758,"mean_force":22.7879,"phase_index":2.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.51829,-0.02425,0.2165]},{"body_a":"peg_socket","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.5473,-0.05343,0.07976],"force_p95":0.0,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.45045,-0.00441,0.09628]}],"total_contact_groups":11},"final_pose_error":0.09075,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53648,-0.02339,0.025],"final_tcp_position":[0.51818,-0.02376,0.21666],"realised_fixture_position":[0.53648,-0.02339,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53648,-0.02339,0.08]},"peak_contact_force":944.68465,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.51237,-0.01676,0.17702],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.09923,"object_to_goal_dist_start":0.26034,"object_z_max":0.34482,"peak_contact_force":271.37759,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":566.0,"raw_peak_contact_force":944.68465,"tcp_end":[0.47743,-0.01713,0.19648],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":273.0,"n_steps_budget":690.0,"object_pos_end":[0.55583,-0.0243,0.20267],"object_pos_start":[0.51237,-0.01676,0.17702],"object_to_goal_dist_end":0.13695,"object_to_goal_dist_start":0.09923,"object_z_max":0.20212,"peak_contact_force":208.34718,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":210.0,"raw_peak_contact_force":629.34202,"tcp_end":[0.51823,-0.02433,0.21632],"tcp_start":[0.47743,-0.01713,0.19648],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":2.0,"n_steps_budget":840.0,"object_pos_end":[0.55606,-0.02396,0.20347],"object_pos_start":[0.55583,-0.0243,0.20267],"object_to_goal_dist_end":0.1377,"object_to_goal_dist_start":0.13695,"object_z_max":0.20313,"peak_contact_force":45.5758,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":45.5758,"tcp_end":[0.5184,-0.02404,0.21695],"tcp_start":[0.51823,-0.02433,0.21632],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":5.0,"n_steps_budget":1000.0,"object_pos_end":[0.55604,-0.02377,0.20375],"object_pos_start":[0.55606,-0.02396,0.20347],"object_to_goal_dist_end":0.13791,"object_to_goal_dist_start":0.1377,"object_z_max":0.20381,"peak_contact_force":227.02105,"phase_name":"insert","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":5.0,"raw_peak_contact_force":227.02105,"tcp_end":[0.51818,-0.02376,0.21666],"tcp_start":[0.51823,-0.02382,0.21685],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```