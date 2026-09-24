## Search State

- **Seed**: 9
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | align → approach → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.0485 | 0.86 | ✅ accepted |
| 6 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.1883 | 0.86 | ❌ rejected |
| 5 | align → approach → descend → contact → insert → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.1036 | 0.86 | ✅ accepted |
| 4 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.2486 | 0.86 | ✅ accepted |
| 3 | align → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | -0.3310 | 0.00 | ❌ rejected |

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
- Frozen realised-scene SHA-256: `d30c452da2a3cff083d30694df03632a9bb782339e47c14383f7124ad9a32464`
- Frozen object start: [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]
- Frozen task target: [0.5296199363176067, -0.017054623272995572, 0.08]
- Frozen socket pose: [0.5296199363176067, -0.017054623272995572, 0.025] (static fixture for this episode)
- Goal object position: (0.5296199363176067, -0.017054623272995572, 0.025)
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
  frozen_task_target: [0.5296, -0.0171, 0.08]
  frozen_socket_position: [0.5296, -0.0171, 0.025]
  socket_state: static_frozen
  frozen_object_starts: {'peg': [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]}
  frozen_targets: {'socket_entry': [0.5296199363176067, -0.017054623272995572, 0.08]}
  frozen_fixtures: {'peg_socket': [0.5296199363176067, -0.017054623272995572, 0.025]}
  insertion_axis: [0, 0, -1]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  hole_depth_m: 0.05
  force_scale_n: 5
  realized_scene_sha256: d30c452da2a3cff083d30694df03632a9bb782339e47c14383f7124ad9a32464

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

## Current Skill (Q=0.048) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
phases:
- id: align_to_socket
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.12
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: channel_axis
      tolerance: 0.05
  parameters:
    lateral_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    lateral_y:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
- id: descend_to_entry
  type: approach
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.08
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
- id: insert_into_hole
  type: insert
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.03
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    insert_speed:
      type: scalar
      range:
      - 0.01
      - 0.04
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
    insertion_depth:
      type: scalar
      range:
      - 0.02
      - 0.04
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
- id: retract_from_hole
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.1
    orientation:
      mode: keep_current
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **align_to_socket** (`align`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.12]
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings:
    - lateral_x: status=consumed; consumers=target.offset.x (add)
    - lateral_y: status=consumed; consumers=target.offset.y (add)
- **descend_to_entry** (`approach`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.08]
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **insert_into_hole** (`insert`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.03]
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - insert_speed: status=consumed; consumers=generator.speed (replace)
    - insertion_depth: status=consumed; consumers=target.offset.z (replace)
- **retract_from_hole** (`retract`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.048
- **task_score** (E): 0.861
- **fitness_score**: 0.408  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_to_socket | 0.33 | 1.00 | 0.1345 |
| descend_to_entry | 0.33 | 1.00 | 0.0772 |
| insert_into_hole | 0.00 | 1.00 | 0.1094 |
| retract_from_hole | 0.00 | 1.00 | 0.0715 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_to_socket | align | 0.33 / step_budget | (0.500, -0.000, 0.301)→(0.510, 0.058, 0.210) | (0.504, -0.000, 0.340)→(0.534, 0.044, 0.187) | 0.260→0.125 | 1.00 / 1.333 | 296.896 | 3244.007 |
| descend_to_entry | approach | 0.33 / step_budget | (0.510, 0.058, 0.210)→(0.529, 0.019, 0.263) | (0.534, 0.044, 0.187)→(0.550, 0.015, 0.233) | 0.125→0.163 | 1.00 / 1.333 | 291.460 | 391.103 |
| insert_into_hole | insert | 0.00 / step_budget | (0.529, 0.019, 0.263)→(0.506, -0.012, 0.310) | (0.550, 0.015, 0.233)→(0.522, -0.004, 0.274) | 0.163→0.200 | 1.00 / 2.000 | 171.262 | 2402.323 |
| retract_from_hole | retract | 0.00 / step_budget | (0.506, -0.012, 0.310)→(0.547, -0.013, 0.287) | (0.522, -0.004, 0.274)→(0.569, -0.009, 0.255) | 0.200→0.190 | 1.00 / 1.333 | 366.244 | 776.109 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.868
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.868
- phase_score: 0.153
- phase_breakdown.contact_score: 0.000
- phase_breakdown.approach_score: 0.083
- phase_breakdown.insert_score: 0.271
- phase_breakdown.align_score: 0.005

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.439
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.868
- **Median Q (composite search score)**: 0.069
- **K-run variance**: 0.0013
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Parameters at upper bound**: align_to_socket.lateral_x
- **Final σ (mean)**: 0.392


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `9cec5bdbb03cce7c3c09816ace5d94f97b8f61fe750542a4a790173a53dc00b4`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `aa1cc88294efeb3bf6fcf727f27d837e44fca2942932baa7feaaed37c752b2f3`; realized-scene SHA-256: `d30c452da2a3cff083d30694df03632a9bb782339e47c14383f7124ad9a32464`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.52962,-0.01705,0.025]},{"name":"target","value":[0.52962,-0.01705,0.025]},{"name":"socket","value":[0.52962,-0.01705,0.025]},{"name":"goal","value":[0.52962,-0.01705,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,-0.01705,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.52962,-0.01705,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.46897,"average_solve_count":145.0,"average_success_count":145.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_socket.lateral_x":0.00738,"align_to_socket.lateral_y":-0.00371,"descend_to_entry.descend_speed":0.04208,"insert_into_hole.insert_speed":0.0292,"insert_into_hole.insertion_depth":0.03576,"retract_from_hole.retract_speed":0.10514},"optimized_scores":{"best_composite_score":0.06859,"best_fitness_score":0.42859,"best_task_score":0.86376},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":6.0,"contact_point_centroid":[0.47027,-0.00243,0.07922],"force_p95":970.01363,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1008.96348,"mean_force":430.95676,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.45989,-0.00242,0.0907]},{"body_a":"peg_socket","body_b":"link7","contact_count":59.0,"contact_point_centroid":[0.57485,-0.00805,0.07938],"force_p95":547.17606,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":983.93879,"mean_force":283.5018,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.46393,-0.00874,0.13864]},{"body_a":"peg_socket","body_b":"link6","contact_count":727.0,"contact_point_centroid":[0.58953,-0.00937,0.07983],"force_p95":381.29721,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":934.27918,"mean_force":264.04558,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.46336,-0.00422,0.18216]},{"body_a":"peg_socket","body_b":"link6","contact_count":694.0,"contact_point_centroid":[0.568,-0.02847,0.07987],"force_p95":714.38604,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":817.51931,"mean_force":503.81555,"phase_index":3.0,"phase_name":"retract_from_hole","phase_type":"retract","tcp_position_centroid":[0.50311,-0.02286,0.32992]},{"body_a":"peg_socket","body_b":"link6","contact_count":318.0,"contact_point_centroid":[0.54682,0.01333,0.07991],"force_p95":692.05675,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":746.81322,"mean_force":430.09769,"phase_index":3.0,"phase_name":"retract_from_hole","phase_type":"retract","tcp_position_centroid":[0.4607,-0.0174,0.32903]},{"body_a":"peg_socket","body_b":"link6","contact_count":152.0,"contact_point_centroid":[0.55207,-0.06305,0.07981],"force_p95":660.78178,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":742.44786,"mean_force":340.81352,"phase_index":3.0,"phase_name":"retract_from_hole","phase_type":"retract","tcp_position_centroid":[0.52144,-0.0226,0.3285]},{"body_a":"peg_socket","body_b":"link6","contact_count":970.0,"contact_point_centroid":[0.56058,-0.01955,0.07994],"force_p95":506.5202,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":675.62683,"mean_force":382.30244,"phase_index":2.0,"phase_name":"insert_into_hole","phase_type":"insert","tcp_position_centroid":[0.49201,-0.03928,0.33864]},{"body_a":"peg_socket","body_b":"link6","contact_count":90.0,"contact_point_centroid":[0.49962,-0.03595,0.07993],"force_p95":459.63981,"geom_a":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":652.48377,"mean_force":265.37947,"phase_index":3.0,"phase_name":"retract_from_hole","phase_type":"retract","tcp_position_centroid":[0.47936,-0.042,0.33553]},{"body_a":"peg_socket","body_b":"link6","contact_count":978.0,"contact_point_centroid":[0.5896,-0.04038,0.07994],"force_p95":278.662,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":396.28883,"mean_force":232.02637,"phase_index":1.0,"phase_name":"descend_to_entry","phase_type":"approach","tcp_position_centroid":[0.54489,0.00781,0.33242]},{"body_a":"peg_socket","body_b":"link7","contact_count":16.0,"contact_point_centroid":[0.54627,0.01331,0.079],"force_p95":178.67437,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":341.96086,"mean_force":39.76662,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.4497,-0.00291,0.09841]},{"body_a":"peg_socket","body_b":"link6","contact_count":664.0,"contact_point_centroid":[0.49962,-0.02877,0.07998],"force_p95":282.42322,"geom_a":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":318.48029,"mean_force":212.11284,"phase_index":2.0,"phase_name":"insert_into_hole","phase_type":"insert","tcp_position_centroid":[0.48348,-0.04477,0.33669]}],"total_contact_groups":11},"final_pose_error":0.20806,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.5751,-0.0088,0.32786],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":1008.96348,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":933.0,"n_steps_budget":1000.0,"object_pos_end":[0.51555,0.04067,0.23677],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.1627,"object_to_goal_dist_start":0.26034,"object_z_max":0.34477,"peak_contact_force":303.57933,"phase_name":"align_to_socket","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":808.0,"raw_peak_contact_force":1008.96348,"tcp_end":[0.49187,0.05476,0.26576],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55715,0.00272,0.29851],"object_pos_start":[0.51555,0.04067,0.23677],"object_to_goal_dist_end":0.22588,"object_to_goal_dist_start":0.1627,"object_z_max":0.29851,"peak_contact_force":222.02867,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":978.0,"raw_peak_contact_force":396.28883,"tcp_end":[0.54377,0.00722,0.33594],"tcp_start":[0.49187,0.05476,0.26576],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49409,-0.03433,0.2993],"object_pos_start":[0.55715,0.00272,0.29851],"object_to_goal_dist_end":0.22205,"object_to_goal_dist_start":0.22588,"object_z_max":0.30905,"peak_contact_force":0.0,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1634.0,"raw_peak_contact_force":675.62683,"tcp_end":[0.48051,-0.04201,0.33613],"tcp_start":[0.54377,0.00722,0.33594],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59377,-0.0098,0.2925],"object_pos_start":[0.49409,-0.03433,0.2993],"object_to_goal_dist_end":0.23247,"object_to_goal_dist_start":0.22205,"object_z_max":0.29931,"peak_contact_force":383.77525,"phase_name":"retract_from_hole","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1254.0,"raw_peak_contact_force":817.51931,"tcp_end":[0.5751,-0.0088,0.32786],"tcp_start":[0.48051,-0.04201,0.33613],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `688a3926bc1208c752fc2d1535fab63bd957243e02b13eac53840dc266efeb6b`; realized-scene SHA-256: `3df42339bb213b8d34da19ed0076dd8b56ad93b79493c43fb7ab2bb6b5f8a158`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.53648,-0.02339,0.025]},{"name":"target","value":[0.53648,-0.02339,0.025]},{"name":"socket","value":[0.53648,-0.02339,0.025]},{"name":"goal","value":[0.53648,-0.02339,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.53648,-0.02339,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.53648,-0.02339,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.55172,"average_solve_count":145.0,"average_success_count":145.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_socket.lateral_x":0.02,"align_to_socket.lateral_y":-0.00102,"descend_to_entry.descend_speed":0.06246,"insert_into_hole.insert_speed":0.02355,"insert_into_hole.insertion_depth":0.03727,"retract_from_hole.retract_speed":0.11349},"optimized_scores":{"best_composite_score":0.07886,"best_fitness_score":0.43886,"best_task_score":0.86794},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":31.0,"contact_point_centroid":[0.54766,0.00714,0.078],"force_p95":827.79412,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":948.8777,"mean_force":206.33398,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.45237,-0.00319,0.10417]},{"body_a":"peg_socket","body_b":"link6","contact_count":927.0,"contact_point_centroid":[0.57525,-0.02711,0.07989],"force_p95":747.33122,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":844.51564,"mean_force":504.6918,"phase_index":3.0,"phase_name":"retract_from_hole","phase_type":"retract","tcp_position_centroid":[0.53209,-0.02119,0.33009]},{"body_a":"attachment","body_b":"peg_socket","contact_count":2.0,"contact_point_centroid":[0.47651,-0.00268,0.07994],"force_p95":827.84669,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":829.11359,"mean_force":816.44462,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.46731,-0.00268,0.09234]},{"body_a":"peg_socket","body_b":"link6","contact_count":579.0,"contact_point_centroid":[0.56543,0.01231,0.07993],"force_p95":388.96363,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":581.75465,"mean_force":216.71424,"phase_index":2.0,"phase_name":"insert_into_hole","phase_type":"insert","tcp_position_centroid":[0.50737,-0.02717,0.33467]},{"body_a":"peg_socket","body_b":"link6","contact_count":793.0,"contact_point_centroid":[0.59626,-0.01216,0.07982],"force_p95":366.13393,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":561.36899,"mean_force":261.4184,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.46725,0.00558,0.16918]},{"body_a":"peg_socket","body_b":"link6","contact_count":135.0,"contact_point_centroid":[0.56422,0.00662,0.0798],"force_p95":318.45286,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":543.11543,"mean_force":191.39666,"phase_index":3.0,"phase_name":"retract_from_hole","phase_type":"retract","tcp_position_centroid":[0.51011,-0.0221,0.33329]},{"body_a":"peg_socket","body_b":"link6","contact_count":459.0,"contact_point_centroid":[0.50592,-0.02407,0.07996],"force_p95":162.59068,"geom_a":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":516.71029,"mean_force":99.26165,"phase_index":2.0,"phase_name":"insert_into_hole","phase_type":"insert","tcp_position_centroid":[0.50738,-0.02691,0.33464]},{"body_a":"peg_socket","body_b":"link6","contact_count":958.0,"contact_point_centroid":[0.58092,0.01725,0.07992],"force_p95":333.07284,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":435.79086,"mean_force":235.88693,"phase_index":2.0,"phase_name":"insert_into_hole","phase_type":"insert","tcp_position_centroid":[0.5221,-0.01679,0.33847]},{"body_a":"peg_socket","body_b":"link6","contact_count":83.0,"contact_point_centroid":[0.50645,-0.02493,0.07983],"force_p95":323.31045,"geom_a":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":404.65715,"mean_force":103.28512,"phase_index":3.0,"phase_name":"retract_from_hole","phase_type":"retract","tcp_position_centroid":[0.50979,-0.02227,0.33356]},{"body_a":"peg_socket","body_b":"link6","contact_count":952.0,"contact_point_centroid":[0.59645,-0.02721,0.07993],"force_p95":309.04192,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":403.20434,"mean_force":265.28816,"phase_index":1.0,"phase_name":"descend_to_entry","phase_type":"approach","tcp_position_centroid":[0.58818,0.02448,0.33338]},{"body_a":"peg_socket","body_b":"link7","contact_count":39.0,"contact_point_centroid":[0.5709,-0.00275,0.07885],"force_p95":208.69805,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":216.45173,"mean_force":46.90144,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.45296,-0.00326,0.10939]},{"body_a":"peg_socket","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.54761,-0.05342,0.07981],"force_p95":0.0,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.4506,-0.00306,0.0956]}],"total_contact_groups":12},"final_pose_error":0.19374,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53648,-0.02339,0.025],"final_tcp_position":[0.56349,-0.03501,0.3165],"realised_fixture_position":[0.53648,-0.02339,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53648,-0.02339,0.08]},"peak_contact_force":948.8777,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":963.0,"n_steps_budget":1000.0,"object_pos_end":[0.58391,0.09304,0.21899],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.18713,"object_to_goal_dist_start":0.26034,"object_z_max":0.34482,"peak_contact_force":305.78366,"phase_name":"align_to_socket","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":871.0,"raw_peak_contact_force":948.8777,"tcp_end":[0.57296,0.12244,0.2438],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58965,0.03637,0.29576],"object_pos_start":[0.58391,0.09304,0.21899],"object_to_goal_dist_end":0.23646,"object_to_goal_dist_start":0.18713,"object_z_max":0.30089,"peak_contact_force":322.15895,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":952.0,"raw_peak_contact_force":403.20434,"tcp_end":[0.57815,0.04054,0.33384],"tcp_start":[0.57296,0.12244,0.2438],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52463,-0.01427,0.29846],"object_pos_start":[0.58965,0.03637,0.29576],"object_to_goal_dist_end":0.22031,"object_to_goal_dist_start":0.23646,"object_z_max":0.30959,"peak_contact_force":276.78445,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1996.0,"raw_peak_contact_force":581.75465,"tcp_end":[0.50934,-0.02275,0.33444],"tcp_start":[0.57815,0.04054,0.33384],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58855,-0.03073,0.28562],"object_pos_start":[0.52463,-0.01427,0.29846],"object_to_goal_dist_end":0.22597,"object_to_goal_dist_start":0.22031,"object_z_max":0.29873,"peak_contact_force":294.89418,"phase_name":"retract_from_hole","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1145.0,"raw_peak_contact_force":844.51564,"tcp_end":[0.56349,-0.03501,0.3165],"tcp_start":[0.50934,-0.02275,0.33444],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a628d07ffd5fd1634a1f36dba43ee92c313515a1a075bf67fe2ba29ce8996148`; realized-scene SHA-256: `025a988ff91962c08fa963a737fe7ec85e866c8c15bf8e1bf01c5bb6961db318`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.47029,-6e-05,0.025]},{"name":"target","value":[0.47029,-6e-05,0.025]},{"name":"socket","value":[0.47029,-6e-05,0.025]},{"name":"goal","value":[0.47029,-6e-05,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.47029,-6e-05,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.47029,-6e-05,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.312,"average_solve_count":125.0,"average_success_count":125.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_socket.lateral_x":0.01999,"align_to_socket.lateral_y":-0.00717,"descend_to_entry.descend_speed":0.02541,"insert_into_hole.insert_speed":0.0306,"insert_into_hole.insertion_depth":0.03136,"retract_from_hole.retract_speed":0.10057},"optimized_scores":{"best_composite_score":-0.00206,"best_fitness_score":0.35794,"best_task_score":0.85062},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":509.0,"contact_point_centroid":[0.52963,-0.00115,0.07998],"force_p95":104.10975,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":7774.18052,"mean_force":216.90292,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.46369,-0.0014,0.11785]},{"body_a":"world","body_b":"link5","contact_count":474.0,"contact_point_centroid":[0.51797,0.1145,-4e-05],"force_p95":2303.32756,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":5949.58758,"mean_force":686.55269,"phase_index":2.0,"phase_name":"insert_into_hole","phase_type":"insert","tcp_position_centroid":[0.52771,0.02172,0.25486]},{"body_a":"peg_socket","body_b":"link7","contact_count":809.0,"contact_point_centroid":[0.53002,-0.00516,0.06509],"force_p95":333.08254,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":5302.63236,"mean_force":350.57177,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.46064,-0.00114,0.11394]},{"body_a":"peg_socket","body_b":"link5","contact_count":481.0,"contact_point_centroid":[0.50693,0.05964,0.05474],"force_p95":1865.6703,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":4145.86775,"mean_force":507.52438,"phase_index":2.0,"phase_name":"insert_into_hole","phase_type":"insert","tcp_position_centroid":[0.52784,0.02113,0.25453]},{"body_a":"attachment","body_b":"peg_socket","contact_count":16.0,"contact_point_centroid":[0.43902,0.00336,0.07977],"force_p95":2418.80594,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2453.30839,"mean_force":1254.60094,"phase_index":0.0,"phase_name":"align_to_socket","phase_type":"align","tcp_position_centroid":[0.43705,-0.00083,0.08379]},{"body_a":"peg_socket","body_b":"link5","contact_count":181.0,"contact_point_centroid":[0.50802,0.05933,0.04995],"force_p95":628.05059,"geom_a":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1049.27022,"mean_force":205.98869,"phase_index":2.0,"phase_name":"insert_into_hole","phase_type":"insert","tcp_position_centroid":[0.52861,0.01026,0.24948]},{"body_a":"peg_socket","body_b":"link5","contact_count":61.0,"contact_point_centroid":[0.5001,0.05936,0.06203],"force_p95":893.09064,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1004.32683,"mean_force":133.28462,"phase_index":2.0,"phase_name":"insert_into_hole","phase_type":"insert","tcp_position_centroid":[0.53308,-0.0043,0.24157]},{"body_a":"world","body_b":"link5","contact_count":803.0,"contact_point_centroid":[0.53526,0.1259,-0.00012],"force_p95":607.85154,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":666.29145,"mean_force":462.61883,"phase_index":3.0,"phase_name":"retract_from_hole","phase_type":"retract","tcp_position_centroid":[0.51272,0.01191,0.23962]},{"body_a":"world","body_b":"link6","contact_count":244.0,"contact_point_centroid":[0.67556,0.03539,-0.00014],"force_p95":440.59858,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":564.21982,"mean_force":269.76357,"phase_index":2.0,"phase_name":"insert_into_hole","phase_type":"insert","tcp_position_centroid":[0.48277,-0.03752,0.1337]},{"body_a":"peg_socket","body_b":"link7","contact_count":308.0,"contact_point_centroid":[0.53016,0.01103,0.066],"force_p95":411.4379,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":527.91246,"mean_force":346.4819,"phase_index":2.0,"phase_name":"insert_into_hole","phase_type":"insert","tcp_position_centroid":[0.46635,-0.00944,0.11847]},{"body_a":"attachment","body_b":"peg_socket","contact_count":137.0,"contact_point_centroid":[0.53028,0.00021,0.07998],"force_p95":238.87228,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":449.73031,"mean_force":170.51158,"phase_index":2.0,"phase_name":"insert_into_hole","phase_type":"insert","tcp_position_centroid":[0.46699,-0.01243,0.11815]},{"body_a":"peg_socket","body_b":"link7","contact_count":222.0,"contact_point_centroid":[0.5302,-0.00421,0.06378],"force_p95":348.12477,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":373.81704,"mean_force":295.3278,"phase_index":1.0,"phase_name":"descend_to_entry","phase_type":"approach","tcp_position_centroid":[0.46467,0.00366,0.11876]},{"body_a":"world","body_b":"link6","contact_count":17.0,"contact_point_centroid":[0.68276,-0.0008,-0.00014],"force_p95":327.5643,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":352.33961,"mean_force":179.7603,"phase_index":1.0,"phase_name":"descend_to_entry","phase_type":"approach","tcp_position_centroid":[0.4653,-0.00166,0.11974]},{"body_a":"peg_socket","body_b":"link5","contact_count":10.0,"contact_point_centroid":[0.50738,0.05992,0.05535],"force_p95":248.2546,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":330.79419,"mean_force":133.12019,"phase_index":3.0,"phase_name":"retract_from_hole","phase_type":"retract","tcp_position_centroid":[0.5287,0.02967,0.25818]},{"body_a":"attachment","body_b":"peg_socket","contact_count":197.0,"contact_point_centroid":[0.53027,0.00128,0.07997],"force_p95":285.96774,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":306.40424,"mean_force":152.60122,"phase_index":1.0,"phase_name":"descend_to_entry","phase_type":"approach","tcp_position_centroid":[0.4646,0.00431,0.11864]},{"body_a":"world","body_b":"link6","contact_count":22.0,"contact_point_centroid":[0.63149,0.05964,-0.00011],"force_p95":60.96351,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":69.03522,"mean_force":43.4415,"phase_index":3.0,"phase_name":"retract_from_hole","phase_type":"retract","tcp_position_centroid":[0.50139,0.00408,0.21779]}],"total_contact_groups":17},"final_pose_error":0.09767,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.47029,-6e-05,0.025],"final_tcp_position":[0.50126,0.004,0.21753],"realised_fixture_position":[0.47029,-6e-05,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.47029,-6e-05,0.08]},"peak_contact_force":7774.18052,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":903.0,"n_steps_budget":990.0,"object_pos_end":[0.50261,-0.00227,0.10582],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.02605,"object_to_goal_dist_start":0.26034,"object_z_max":0.34445,"peak_contact_force":281.3251,"phase_name":"align_to_socket","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1352.0,"raw_peak_contact_force":7774.18052,"tcp_end":[0.46496,-0.00255,0.11933],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":223.0,"n_steps_budget":600.0,"object_pos_end":[0.50275,0.00547,0.10572],"object_pos_start":[0.50261,-0.00227,0.10582],"object_to_goal_dist_end":0.02644,"object_to_goal_dist_start":0.02605,"object_z_max":0.10609,"peak_contact_force":330.19366,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":436.0,"raw_peak_contact_force":373.81704,"tcp_end":[0.46513,0.00788,0.11911],"tcp_start":[0.46496,-0.00255,0.11933],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54779,0.03768,0.22395],"object_pos_start":[0.50275,0.00547,0.10572],"object_to_goal_dist_end":0.15628,"object_to_goal_dist_start":0.02644,"object_z_max":0.22395,"peak_contact_force":237.00252,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1886.0,"raw_peak_contact_force":5949.58758,"tcp_end":[0.52887,0.02992,0.25832],"tcp_start":[0.46513,0.00788,0.11911],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":843.0,"n_steps_budget":930.0,"object_pos_end":[0.52592,0.01284,0.1873],"object_pos_start":[0.54779,0.03768,0.22395],"object_to_goal_dist_end":0.11113,"object_to_goal_dist_start":0.15628,"object_z_max":0.22401,"peak_contact_force":420.06367,"phase_name":"retract_from_hole","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":835.0,"raw_peak_contact_force":666.29145,"tcp_end":[0.50126,0.004,0.21753],"tcp_start":[0.52887,0.02992,0.25832],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```