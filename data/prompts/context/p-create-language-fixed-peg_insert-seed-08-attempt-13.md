## Search State

- **Seed**: 8
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → align → contact → insert → retract | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | time_limit | 8 | 0.1049 | 0.85 | ❌ rejected |
| 12 | approach → approach → contact → insert | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | 3 | 0.4813 | 0.86 | ❌ rejected |
| 11 | approach → approach → contact → insert | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | 3 | 0.4818 | 0.86 | ❌ rejected |
| 10 | approach → align → contact → insert | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8 | 0.1481 | 0.84 | ❌ rejected |
| 9 | approach → align → contact → insert | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 4 | 0.4593 | 0.85 | ❌ rejected |

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

## Current Skill (Q=0.105) — your mutation base

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

- **Composite score**: 0.105
- **task_score** (E): 0.849
- **fitness_score**: 0.345  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.490

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_arc | 0.00 | 1.00 | 0.1310 |
| align_entry | 1.00 | 0.33 | 0.0327 |
| contact_probe | 1.00 | 1.00 | 0.0001 |
| insert_down | 0.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_arc | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.457, -0.002, 0.179) | (0.504, -0.000, 0.340)→(0.494, -0.002, 0.163) | 0.260→0.087 | 1.00 / 1.000 | 258.212 | 1542.752 |
| align_entry | align | 1.00 / step_budget | (0.457, -0.002, 0.179)→(0.488, -0.002, 0.171) | (0.494, -0.002, 0.163)→(0.524, -0.002, 0.154) | 0.087→0.083 | 0.33 / 0.333 | 98.616 | 295.391 |
| contact_probe | contact | 1.00 / force_exceeded | (0.488, -0.002, 0.171)→(0.488, -0.002, 0.171) | (0.524, -0.002, 0.154)→(0.524, -0.002, 0.154) | 0.083→0.083 | 1.00 / 1.000 | 654.257 | 165.726 |
| insert_down | insert | 0.00 / guard_failure | (0.488, -0.002, 0.171)→(0.488, -0.002, 0.171) | (0.524, -0.002, 0.154)→(0.524, -0.002, 0.154) | 0.083→0.083 | 1.00 / 1.000 | 161.981 | 161.981 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.868
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.868
- phase_score: 0.008
- phase_breakdown.insert_score: 0.009
- phase_breakdown.approach_score: 0.006
- phase_breakdown.contact_score: 0.008
- phase_breakdown.align_score: 0.002

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.352
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.869
- **Median Q (composite search score)**: 0.112
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.388


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.45238,"average_solve_count":42.0,"average_success_count":42.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_entry.align_offset_x":-0.02,"align_entry.align_offset_y":-0.00526,"approach_arc.approach_speed":0.09621,"approach_arc.arc_height":0.09995,"contact_probe.contact_force":14.37186,"insert_down.insert_force_threshold":35.85732,"insert_down.insert_speed":0.04123,"insert_down.insertion_distance":0.06622},"optimized_scores":{"best_composite_score":0.09138,"best_fitness_score":0.33138,"best_task_score":0.8094},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":114.0,"contact_point_centroid":[0.54171,0.0147,0.07908],"force_p95":648.1316,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1088.62878,"mean_force":302.8489,"phase_index":0.0,"phase_name":"approach_arc","phase_type":"approach","tcp_position_centroid":[0.4336,0.01667,0.14225]},{"body_a":"peg_socket","body_b":"link6","contact_count":302.0,"contact_point_centroid":[0.54608,0.02807,0.07985],"force_p95":311.14302,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1049.9202,"mean_force":295.3727,"phase_index":0.0,"phase_name":"approach_arc","phase_type":"approach","tcp_position_centroid":[0.44272,0.0267,0.18811]},{"body_a":"attachment","body_b":"peg_socket","contact_count":10.0,"contact_point_centroid":[0.44188,0.01159,0.07909],"force_p95":497.60764,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":904.74116,"mean_force":90.47412,"phase_index":0.0,"phase_name":"approach_arc","phase_type":"approach","tcp_position_centroid":[0.43789,0.01156,0.09263]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.5461,0.03931,0.07993],"force_p95":439.89136,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":439.89136,"mean_force":439.89136,"phase_index":2.0,"phase_name":"contact_probe","phase_type":"contact","tcp_position_centroid":[0.4776,0.03445,0.1922]},{"body_a":"peg_socket","body_b":"link7","contact_count":123.0,"contact_point_centroid":[0.54602,0.03952,0.07985],"force_p95":303.07521,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":342.48903,"mean_force":268.07249,"phase_index":1.0,"phase_name":"align_entry","phase_type":"align","tcp_position_centroid":[0.47529,0.03373,0.19724]},{"body_a":"peg_socket","body_b":"link6","contact_count":394.0,"contact_point_centroid":[0.5461,0.03218,0.07993],"force_p95":252.25344,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":298.09981,"mean_force":174.65804,"phase_index":1.0,"phase_name":"align_entry","phase_type":"align","tcp_position_centroid":[0.46196,0.03111,0.20203]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.5461,0.03929,0.07993],"force_p95":120.97843,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":120.97843,"mean_force":120.97843,"phase_index":3.0,"phase_name":"insert_down","phase_type":"insert","tcp_position_centroid":[0.47759,0.03445,0.19215]}],"total_contact_groups":7},"final_pose_error":0.06617,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.47759,0.03444,0.19211],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"peak_contact_force":1088.62878,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.48385,0.03087,0.1773],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.10335,"object_to_goal_dist_start":0.26034,"object_z_max":0.34407,"peak_contact_force":298.32628,"phase_name":"approach_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":426.0,"raw_peak_contact_force":1088.62878,"tcp_end":[0.4511,0.02986,0.20025],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.50861,0.03543,0.16696],"object_pos_start":[0.48385,0.03087,0.1773],"object_to_goal_dist_end":0.09429,"object_to_goal_dist_start":0.10335,"object_z_max":0.17841,"peak_contact_force":295.84923,"phase_name":"align_entry","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":517.0,"raw_peak_contact_force":342.48903,"tcp_end":[0.4776,0.03445,0.1922],"tcp_start":[0.4511,0.02986,0.20025],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50861,0.03542,0.16691],"object_pos_start":[0.50861,0.03543,0.16696],"object_to_goal_dist_end":0.09425,"object_to_goal_dist_start":0.09429,"object_z_max":0.16696,"peak_contact_force":439.89136,"phase_name":"contact_probe","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":439.89136,"tcp_end":[0.47759,0.03445,0.19215],"tcp_start":[0.4776,0.03445,0.1922],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50862,0.03542,0.16688],"object_pos_start":[0.50861,0.03542,0.16691],"object_to_goal_dist_end":0.09422,"object_to_goal_dist_start":0.09425,"object_z_max":0.16691,"peak_contact_force":120.97843,"phase_name":"insert_down","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":120.97843,"tcp_end":[0.47759,0.03444,0.19211],"tcp_start":[0.47759,0.03445,0.19215],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":9.0,"average_failure_rate":0.2093,"average_mean_iterations":47.09302,"average_solve_count":43.0,"average_success_count":34.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_entry.align_offset_x":0.00299,"align_entry.align_offset_y":0.00377,"approach_arc.approach_speed":0.063,"approach_arc.arc_height":0.0432,"contact_probe.contact_force":8.34216,"insert_down.insert_force_threshold":26.95378,"insert_down.insert_speed":0.03184,"insert_down.insertion_distance":0.0559},"optimized_scores":{"best_composite_score":0.11159,"best_fitness_score":0.35159,"best_task_score":0.86912},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link6","contact_count":331.0,"contact_point_centroid":[0.58959,-0.01845,0.07983],"force_p95":275.73082,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2595.48937,"mean_force":256.19563,"phase_index":0.0,"phase_name":"approach_arc","phase_type":"approach","tcp_position_centroid":[0.45933,-0.01564,0.15742]},{"body_a":"peg_socket","body_b":"link7","contact_count":52.0,"contact_point_centroid":[0.57119,-0.01368,0.07823],"force_p95":1000.66892,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2504.78731,"mean_force":330.76847,"phase_index":0.0,"phase_name":"approach_arc","phase_type":"approach","tcp_position_centroid":[0.45906,-0.01249,0.11675]},{"body_a":"attachment","body_b":"peg_socket","contact_count":9.0,"contact_point_centroid":[0.4709,-0.01134,0.07893],"force_p95":559.05102,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":931.75169,"mean_force":103.52797,"phase_index":0.0,"phase_name":"approach_arc","phase_type":"approach","tcp_position_centroid":[0.4643,-0.01127,0.09158]},{"body_a":"peg_socket","body_b":"link7","contact_count":16.0,"contact_point_centroid":[0.55727,-0.04725,0.07887],"force_p95":789.51557,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":853.56244,"mean_force":101.35807,"phase_index":0.0,"phase_name":"approach_arc","phase_type":"approach","tcp_position_centroid":[0.46084,-0.01149,0.09751]},{"body_a":"peg_socket","body_b":"link6","contact_count":105.0,"contact_point_centroid":[0.58961,-0.01861,0.07996],"force_p95":141.00452,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":292.37001,"mean_force":119.25291,"phase_index":1.0,"phase_name":"align_entry","phase_type":"align","tcp_position_centroid":[0.4659,-0.017,0.16354]},{"body_a":"peg_socket","body_b":"link7","contact_count":119.0,"contact_point_centroid":[0.5896,-0.01248,0.07995],"force_p95":124.18108,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":209.48525,"mean_force":104.08676,"phase_index":1.0,"phase_name":"align_entry","phase_type":"align","tcp_position_centroid":[0.48274,-0.01613,0.15873]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.58961,-0.01389,0.07995],"force_p95":101.47412,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":101.47412,"mean_force":101.47412,"phase_index":3.0,"phase_name":"insert_down","phase_type":"insert","tcp_position_centroid":[0.49227,-0.01575,0.15553]},{"body_a":"peg_socket","body_b":"link7","contact_count":11.0,"contact_point_centroid":[0.55699,0.01318,0.07969],"force_p95":12.52056,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":25.04112,"mean_force":2.27647,"phase_index":0.0,"phase_name":"approach_arc","phase_type":"approach","tcp_position_centroid":[0.46095,-0.01141,0.09472]}],"total_contact_groups":8},"final_pose_error":0.05586,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.49224,-0.01574,0.15549],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":2595.48937,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":464.0,"n_steps_budget":630.0,"object_pos_end":[0.49757,-0.017,0.15238],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.07439,"object_to_goal_dist_start":0.26034,"object_z_max":0.34545,"peak_contact_force":236.16108,"phase_name":"approach_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":419.0,"raw_peak_contact_force":2595.48937,"tcp_end":[0.45914,-0.0172,0.16348],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":272.0,"n_steps_budget":600.0,"object_pos_end":[0.53058,-0.01557,0.1439],"object_pos_start":[0.49757,-0.017,0.15238],"object_to_goal_dist_end":0.07253,"object_to_goal_dist_start":0.07439,"object_z_max":0.15265,"peak_contact_force":0.0,"phase_name":"align_entry","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":224.0,"raw_peak_contact_force":292.37001,"tcp_end":[0.49232,-0.01575,0.15558],"tcp_start":[0.45914,-0.0172,0.16348],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.53053,-0.01556,0.14383],"object_pos_start":[0.53058,-0.01557,0.1439],"object_to_goal_dist_end":0.07245,"object_to_goal_dist_start":0.07253,"object_z_max":0.1439,"peak_contact_force":1465.59194,"phase_name":"contact_probe","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49227,-0.01575,0.15553],"tcp_start":[0.49232,-0.01575,0.15558],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.53048,-0.01556,0.14378],"object_pos_start":[0.53053,-0.01556,0.14383],"object_to_goal_dist_end":0.07238,"object_to_goal_dist_start":0.07245,"object_z_max":0.14383,"peak_contact_force":101.47412,"phase_name":"insert_down","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":101.47412,"tcp_end":[0.49224,-0.01574,0.15549],"tcp_start":[0.49227,-0.01575,0.15553],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":8.0,"average_failure_rate":0.18605,"average_mean_iterations":42.4186,"average_solve_count":43.0,"average_success_count":35.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_entry.align_offset_x":-0.01231,"align_entry.align_offset_y":-0.01054,"approach_arc.approach_speed":0.07927,"approach_arc.arc_height":0.08482,"contact_probe.contact_force":10.87424,"insert_down.insert_force_threshold":11.53975,"insert_down.insert_speed":0.03476,"insert_down.insertion_distance":0.06076},"optimized_scores":{"best_composite_score":0.11169,"best_fitness_score":0.35169,"best_task_score":0.86761},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.4767,-0.00992,0.07985],"force_p95":930.32115,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":944.13744,"mean_force":811.61832,"phase_index":0.0,"phase_name":"approach_arc","phase_type":"approach","tcp_position_centroid":[0.46899,-0.00992,0.09285]},{"body_a":"peg_socket","body_b":"link7","contact_count":38.0,"contact_point_centroid":[0.57348,-0.01179,0.07928],"force_p95":506.49741,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":903.77992,"mean_force":202.75037,"phase_index":0.0,"phase_name":"approach_arc","phase_type":"approach","tcp_position_centroid":[0.45333,-0.01173,0.11516]},{"body_a":"peg_socket","body_b":"link6","contact_count":338.0,"contact_point_centroid":[0.59638,-0.01849,0.0798],"force_p95":272.04336,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":481.59305,"mean_force":242.29287,"phase_index":0.0,"phase_name":"approach_arc","phase_type":"approach","tcp_position_centroid":[0.45796,-0.01509,0.15961]},{"body_a":"peg_socket","body_b":"link7","contact_count":14.0,"contact_point_centroid":[0.55199,0.00695,0.07936],"force_p95":323.05021,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":436.80944,"mean_force":63.61654,"phase_index":0.0,"phase_name":"approach_arc","phase_type":"approach","tcp_position_centroid":[0.45559,-0.01084,0.09894]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.59646,-0.02207,0.07996],"force_p95":263.49097,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":263.49097,"mean_force":263.49097,"phase_index":3.0,"phase_name":"insert_down","phase_type":"insert","tcp_position_centroid":[0.49535,-0.02561,0.16402]},{"body_a":"peg_socket","body_b":"link6","contact_count":186.0,"contact_point_centroid":[0.59646,-0.02223,0.07995],"force_p95":146.63972,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":251.31449,"mean_force":127.15465,"phase_index":1.0,"phase_name":"align_entry","phase_type":"align","tcp_position_centroid":[0.47319,-0.02065,0.17199]},{"body_a":"peg_socket","body_b":"link7","contact_count":68.0,"contact_point_centroid":[0.59644,-0.0196,0.07992],"force_p95":143.70048,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":149.24976,"mean_force":126.08599,"phase_index":1.0,"phase_name":"align_entry","phase_type":"align","tcp_position_centroid":[0.49001,-0.02419,0.16642]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.59646,-0.02205,0.07995],"force_p95":57.28679,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":57.28679,"mean_force":57.28679,"phase_index":2.0,"phase_name":"contact_probe","phase_type":"contact","tcp_position_centroid":[0.49529,-0.0256,0.16406]}],"total_contact_groups":8},"final_pose_error":0.0607,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53648,-0.02339,0.025],"final_tcp_position":[0.49538,-0.0256,0.16397],"realised_fixture_position":[0.53648,-0.02339,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53648,-0.02339,0.08]},"peak_contact_force":944.13744,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":461.0,"n_steps_budget":600.0,"object_pos_end":[0.49939,-0.01846,0.16067],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.08276,"object_to_goal_dist_start":0.26034,"object_z_max":0.34521,"peak_contact_force":240.1477,"phase_name":"approach_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":393.0,"raw_peak_contact_force":944.13744,"tcp_end":[0.46166,-0.01859,0.17395],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":298.0,"n_steps_budget":600.0,"object_pos_end":[0.53282,-0.02537,0.15026],"object_pos_start":[0.49939,-0.01846,0.16067],"object_to_goal_dist_end":0.0816,"object_to_goal_dist_start":0.08276,"object_z_max":0.1607,"peak_contact_force":0.0,"phase_name":"align_entry","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":254.0,"raw_peak_contact_force":251.31449,"tcp_end":[0.4953,-0.0256,0.16412],"tcp_start":[0.46166,-0.01859,0.17395],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":2.0,"n_steps_budget":600.0,"object_pos_end":[0.53287,-0.02538,0.15016],"object_pos_start":[0.53282,-0.02537,0.15026],"object_to_goal_dist_end":0.08153,"object_to_goal_dist_start":0.0816,"object_z_max":0.15026,"peak_contact_force":57.28679,"phase_name":"contact_probe","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":57.28679,"tcp_end":[0.49535,-0.02561,0.16402],"tcp_start":[0.4953,-0.0256,0.16412],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.5329,-0.02537,0.15012],"object_pos_start":[0.53287,-0.02538,0.15016],"object_to_goal_dist_end":0.0815,"object_to_goal_dist_start":0.08153,"object_z_max":0.15016,"peak_contact_force":263.49097,"phase_name":"insert_down","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":263.49097,"tcp_end":[0.49538,-0.0256,0.16397],"tcp_start":[0.49535,-0.02561,0.16402],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```